from typing import Optional, List, Dict, Any
from datetime import datetime
import numpy as np
import pandas as pd
import geopandas as gpd
from tqdm import tqdm



from .config import DEFAULT_INDICES
from .indices import compute_indices
from .aggregation import aggregate_field_indices
from .selection import (
    select_snapshots_fractional,
    select_snapshot_fixed_date,
    select_top_n_cloudfree,
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
        snapshot_strategy: str = "fractional",  # 'fractional', 'fixed_date', 'top_n_cloudfree'
        fractions: Optional[List[float]] = None,
        target_date: Optional[str] = None,
        indices: Optional[List[str]] = None,
        bands: Optional[List[str]] = None,
        stac_limit: int = 100,
    ) -> pd.DataFrame:
        """
        Main entry point: returns field-level RS features for given season.
        """
        if indices is None:
            indices = DEFAULT_INDICES



        season_start = datetime.fromisoformat(start_date)
        season_end = datetime.fromisoformat(end_date)



        bbox = gdf_to_bbox(fields)
        items = self.source.search_items(bbox, start_date, end_date, limit=stac_limit)
        if not items:
            raise RuntimeError("No Sentinel-2 items found for given area/date range.")



        # Choose snapshots according to strategy
        if snapshot_strategy == "fractional":
            if fractions is None:
                fractions = np.linspace(0.2, 1.0, n_snapshots).tolist()
            chosen_items = select_snapshots_fractional(items, season_start, season_end, fractions)
        elif snapshot_strategy == "fixed_date":
            if target_date is None:
                raise ValueError("target_date must be provided for 'fixed_date' strategy.")
            dt = datetime.fromisoformat(target_date)
            chosen_item = select_snapshot_fixed_date(items, dt)
            chosen_items = [chosen_item] if chosen_item else []
        elif snapshot_strategy == "top_n_cloudfree":
            chosen_items = select_top_n_cloudfree(items, n_snapshots)
        else:
            raise ValueError(f"Unknown snapshot_strategy: {snapshot_strategy}")



        if not chosen_items:
            raise RuntimeError("No snapshots selected after applying strategy.")



        # Determine bands to fetch: either user-defined or all required for indices
        if bands is None:
            # Collect all bands in assets whose keys start with 'B'
            # (assumes items share same band set)
            sample_assets = chosen_items[0]["assets"]
            bands = sorted([k for k in sample_assets.keys() if k.startswith("B")])



        rows = []



        # Precompute time fractions for each chosen item
        dur = (season_end - season_start).total_seconds()
        item_meta = []
        for it in chosen_items:
            dt = datetime.fromisoformat(it["properties"]["datetime"].replace("Z", ""))
            frac = (dt - season_start).total_seconds() / dur
            frac = float(np.clip(frac, 0.0, 1.0))
            item_meta.append((it, dt, frac))



        for _, field in tqdm(fields.iterrows(), total=len(fields), desc="Fields"):
            field_id = field[field_id_col]
            geom = field.geometry



            index_time_series: Dict[str, List[Dict[str, Any]]] = {idx: [] for idx in indices}



            for it, dt, frac in item_meta:
                # Map requested bands to asset hrefs
                assets = it["assets"]
                band_hrefs = {}
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



            # Aggregate per field
            series = aggregate_field_indices(
                field_id=field_id,
                index_time_series=index_time_series,
                season_start=season_start,
                season_end=season_end,
            )
            rows.append(series)



        return pd.DataFrame(rows)
