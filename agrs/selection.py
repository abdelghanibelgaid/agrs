from typing import List, Dict, Any, Optional
from datetime import datetime

def select_snapshots_fractional(
    items: List[Dict[str, Any]],
    season_start: datetime,
    season_end: datetime,
    fractions: List[float],
) -> List[Dict[str, Any]]:
    """
    Select items closest to given fractions of the season duration.
    items: list of STAC items with 'properties'['datetime'].
    """
    if not items:
        return []

    # Sort by time
    items_sorted = sorted(
        items,
        key=lambda x: datetime.fromisoformat(x["properties"]["datetime"].replace("Z", "")),
    )

    start = season_start
    end = season_end
    dur = (end - start).total_seconds()
    out = []

    for f in fractions:
        target_t = start.timestamp() + f * dur
        best = min(
            items_sorted,
            key=lambda it: abs(
                datetime.fromisoformat(it["properties"]["datetime"].replace("Z", "")).timestamp() - target_t
            ),
        )
        if best not in out:
            out.append(best)

    return out

def select_snapshot_fixed_date(
    items: List[Dict[str, Any]],
    target_date: datetime,
) -> Optional[Dict[str, Any]]:
    """Select single item closest to target_date."""
    if not items:
        return None
    return min(
        items,
        key=lambda it: abs(
            datetime.fromisoformat(it["properties"]["datetime"].replace("Z", "")) - target_date
        ),
    )

def select_top_n_cloudfree(
    items: List[Dict[str, Any]],
    n: int,
    cloud_prop_name: str = "eo:cloud_cover",
) -> List[Dict[str, Any]]:
    """Select N items with lowest cloud cover."""
    if not items or n <= 0:
        return []
    items_with_cloud = [
        it for it in items if cloud_prop_name in it.get("properties", {})
    ]
    items_sorted = sorted(
        items_with_cloud,
        key=lambda it: it["properties"].get(cloud_prop_name, 100.0),
    )
    return items_sorted[:n]
