from typing import Optional, List, Dict, Any, Union, Tuple
from datetime import datetime
import numpy as np
import pandas as pd
import geopandas as gpd
from tqdm import tqdm

from .config import DEFAULT_INDICES, DEFAULT_FRACTIONS
from .indices import compute_indices
from .aggregation import aggregate_field_indices
from .selection import (
    select_snapshots_fractional,
    select_snapshot_fixed_date,
    select_top_n_cloudfree,
    select_snapshots_all,
    select_snapshots_by_dates,
)
from .sources.planetary_computer_source import PlanetaryComputerS2Source
from .utils import gdf_to_bbox, clip_raster_to_geom


class s2agc:
    def __init__(
        self,
        source: str = "planetary_computer",
        max_cloud: float = 0.3,
    ):
        if source != "planetary_computer":
            raise ValueError("Currently only 'planetary_computer' source is supported in MVP.")
        self.source = PlanetaryComputerS2Source(max_cloud=max_cloud)

    def get_features(
        self,
        fields: gpd.GeoDataFrame,
        field_id_col: str,
        start_date: str,
        end_date: str,
        crop: Optional[str] = None,
        n_snapshots: int = 3,
        snapshot_strategy: str = "fractional",  # 'fractional', 'fixed_date', 'top_n_cloudfree', 'all', 'dates'
        fractions: Optional[List[float]] = None,
        target_date: Optional[str] = None,
        key_dates: Optional[List[str]] = None,
        indices: Optional[List[str]] = None,
        bands: Optional[List[str]] = None,
        stac_limit: int = 100,
        return_mode: str = "features",  # 'features', 'bands', 'both'
    ) -> Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]]:
        """
        Main entry point: returns Sentinel-2 features for given season.

        Parameters
        ----------
        fields : GeoDataFrame
            Field geometries (must have `field_id_col` and a geometry column).
        field_id_col : str
            Column name with unique field identifiers.
        start_date, end_date : str
            ISO dates of the season window (inclusive).
        crop : str, optional
            Crop label (currently informational only).
        n_snapshots : int
            Number of snapshots for strategies that need a count.
        snapshot_strategy : str
            One of:
              - 'fractional'       : nearest to temporal fractions (see `fractions`)
              - 'fixed_date'       : nearest to a single `target_date`
              - 'top_n_cloudfree'  : N lowest-cloud items
              - 'all'              : all items in [start_date, end_date]
              - 'dates'            : nearest to a list of `key_dates`
        fractions : list[float], optional
            Temporal fractions in [0,1] (e.g. [0.3, 0.7]); used for 'fractional'.
            If None, DEFAULT_FRACTIONS are used.
        target_date : str, optional
            ISO datetime string for 'fixed_date' strategy.
        key_dates : list[str], optional
            ISO datetime or date strings for 'dates' strategy.
        indices : list[str], optional
            Indices to compute; if None, DEFAULT_INDICES are used.
        bands : list[str], optional
            Band codes to fetch (e.g. ["B02","B03"]); if None, all 'B*' assets are used.
        stac_limit : int
            Max items from STAC search.
        return_mode : {'features', 'bands', 'both'}
            - 'features' (default): returns aggregated index features.
            - 'bands'            : returns per-band summary stats per snapshot.
            - 'both'             : returns (features_df, bands_df).

        Returns
        -------
        DataFrame or (DataFrame, DataFrame)
        """
        if indices is None:
            indices = DEFAULT_INDICES

        season_start = datetime.fromisoformat(start_date)
        season_end = datetime.fromisoformat(end_date)

        bbox = gdf_to_bbox(fields)
        items = self.source.search_items(bbox, start_date, end_date, limit=stac_limit)
        if not items:
            raise RuntimeError("No Sentinel-2 items found for given area/date range.")

        # ------------------------------
        # Snapshot strategy selection
        # ------------------------------
        if snapshot_strategy == "fractional":
            if fractions is None:
                fractions = DEFAULT_FRACTIONS
            chosen_items = select_snapshots_fractional(items, season_start, season_end, fractions)
        elif snapshot_strategy == "fixed_date":
            if target_date is None:
                raise ValueError("target_date must be provided for 'fixed_date' strategy.")
            dt = datetime.fromisoformat(target_date)
            chosen_item = select_snapshot_fixed_date(items, dt)
            chosen_items = [chosen_item] if chosen_item else []
        elif snapshot_strategy == "top_n_cloudfree":
            chosen_items = select_top_n_cloudfree(items, n_snapshots)
        elif snapshot_strategy == "all":
            chosen_items = select_snapshots_all(items)
        elif snapshot_strategy == "dates":
            if not key_dates:
                raise ValueError("key_dates must be provided for 'dates' strategy.")
            date_objs = [datetime.fromisoformat(d) for d in key_dates]
            chosen_items = select_snapshots_by_dates(items, date_objs)
        else:
            raise ValueError(f"Unknown snapshot_strategy: {snapshot_strategy}")

        if not chosen_items:
            raise RuntimeError("No snapshots selected after applying strategy.")

        # ------------------------------
        # Determine bands to fetch
        # ------------------------------
        if bands is None:
            sample_assets = chosen_items[0]["assets"]
            bands = sorted([k for k in sample_assets.keys() if k.startswith("B")])

        feature_rows: List[Dict[str, Any]] = []
        band_rows: List[Dict[str, Any]] = []

        # Precompute time fractions for chosen items
        dur = (season_end - season_start).total_seconds()
        item_meta = []
        for it in chosen_items:
            dt = datetime.fromisoformat(it["properties"]["datetime"].replace("Z", ""))
            frac = (dt - season_start).total_seconds() / dur if dur > 0 else 0.0
            frac = float(np.clip(frac, 0.0, 1.0))
            item_meta.append((it, dt, frac))

        for _, field in tqdm(fields.iterrows(), total=len(fields), desc="Fields"):
            field_id = field[field_id_col]
            geom = field.geometry

            index_time_series: Dict[str, List[Dict[str, Any]]] = {idx: [] for idx in indices}

            for it, dt, frac in item_meta:
                assets = it["assets"]
                band_hrefs: Dict[str, str] = {}
                for b in bands:
                    if b in assets:
                        band_hrefs[b] = assets[b]["href"]

                if not band_hrefs:
                    continue

                # Clip raster bands to field geometry
                band_arrays = clip_raster_to_geom(asset_href=None, geom=geom, bands=band_hrefs)

                # If no overlap (empty dict), skip this snapshot for this field
                if not band_arrays:
                    continue

                # Compute indices
                idx_arrays = compute_indices(band_arrays)

                # Fill index time series (for aggregated features)
                for idx_name in indices:
                    if idx_name not in idx_arrays:
                        continue
                    index_time_series[idx_name].append(
                        {
                            "datetime": dt,
                            "fraction": frac,
                            "array": idx_arrays[idx_name],
                        }
                    )

                # Optional: per-band stats
                if return_mode in ("bands", "both"):
                    stats_row: Dict[str, Any] = {
                        "field_id": field_id,
                        "datetime": dt,
                        "fraction": frac,
                    }
                    for band_code, arr in band_arrays.items():
                        flat = arr.ravel()
                        flat = flat[np.isfinite(flat)]
                        if flat.size == 0:
                            continue
                        stats_row[f"{band_code}_mean"] = float(np.nanmean(flat))
                        stats_row[f"{band_code}_median"] = float(np.nanmedian(flat))
                        stats_row[f"{band_code}_min"] = float(np.nanmin(flat))
                        stats_row[f"{band_code}_max"] = float(np.nanmax(flat))
                        stats_row[f"{band_code}_std"] = float(np.nanstd(flat))
                        stats_row[f"{band_code}_p10"] = float(np.nanpercentile(flat, 10))
                        stats_row[f"{band_code}_p90"] = float(np.nanpercentile(flat, 90))

                    band_rows.append(stats_row)

            # Aggregate per field for index-based features
            if return_mode in ("features", "both"):
                series = aggregate_field_indices(
                    field_id=field_id,
                    index_time_series=index_time_series,
                    season_start=season_start,
                    season_end=season_end,
                )
                feature_rows.append(series)

        features_df = pd.DataFrame(feature_rows) if feature_rows and return_mode in ("features", "both") else pd.DataFrame()
        bands_df = pd.DataFrame(band_rows) if band_rows and return_mode in ("bands", "both") else pd.DataFrame()

        if return_mode == "features":
            return features_df
        elif return_mode == "bands":
            return bands_df
        elif return_mode == "both":
            return features_df, bands_df
        else:
            raise ValueError(f"Unknown return_mode: {return_mode}")
