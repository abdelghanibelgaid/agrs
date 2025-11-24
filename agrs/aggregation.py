from typing import Dict, List, Tuple
import numpy as np
import pandas as pd

from .config import DEFAULT_SUMMARY_STATS, DEFAULT_STAGE_BOUNDS

def summarize_array(arr: np.ndarray, stats: List[str]) -> Dict[str, float]:
    arr_flat = arr[np.isfinite(arr)].ravel()
    if arr_flat.size == 0:
        return {s: np.nan for s in stats}

    out = {}
    if "mean" in stats:
        out["mean"] = float(np.mean(arr_flat))
    if "median" in stats:
        out["median"] = float(np.median(arr_flat))
    if "min" in stats:
        out["min"] = float(np.min(arr_flat))
    if "max" in stats:
        out["max"] = float(np.max(arr_flat))
    if "std" in stats:
        out["std"] = float(np.std(arr_flat))
    return out

def stage_for_fraction(
    frac: float,
    stage_bounds: Dict[str, Tuple[float, float]] = DEFAULT_STAGE_BOUNDS,
) -> str:
    for name, (lo, hi) in stage_bounds.items():
        if lo <= frac < hi:
            return name
    return "other"

def aggregate_field_indices(
    field_id: str,
    index_time_series: Dict[str, List[Dict]],
    season_start,
    season_end,
    summary_stats: List[str] = None,
    stage_bounds: Dict[str, Tuple[float, float]] = None,
) -> pd.Series:
    """
    index_time_series: dict index_name -> list of dicts:
        {"datetime": dt, "fraction": f, "array": arr_field}
    Returns a pd.Series with columns like NDVI_early_mean, NDVI_mid_max, ...
    """
    if summary_stats is None:
        summary_stats = DEFAULT_SUMMARY_STATS
    if stage_bounds is None:
        stage_bounds = DEFAULT_STAGE_BOUNDS

    data = {
        "field_id": field_id,
        "season_start": season_start,
        "season_end": season_end,
    }

    for index_name, entries in index_time_series.items():
        # group arrays by stage
        stage_arrays = {stage: [] for stage in stage_bounds.keys()}
        for e in entries:
            f = e["fraction"]
            arr = e["array"]
            stage = stage_for_fraction(f, stage_bounds)
            if stage in stage_arrays:
                stage_arrays[stage].append(arr)

        # compute stats per stage
        for stage, arr_list in stage_arrays.items():
            if not arr_list:
                for stat in summary_stats:
                    col = f"{index_name}_{stage}_{stat}"
                    data[col] = float("nan")
                continue

            # combine all arrays in stage (stack, then aggregate)
            stacked = np.stack(arr_list, axis=0)
            # reduce over time and space (flatten)
            # simple approach: average over time first, then stats over space
            mean_over_time = np.nanmean(stacked, axis=0)
            stats_dict = summarize_array(mean_over_time, summary_stats)

            for stat, val in stats_dict.items():
                col = f"{index_name}_{stage}_{stat}"
                data[col] = val

    return pd.Series(data)
