from __future__ import annotations
from typing import List, Sequence, Mapping, Any
from datetime import datetime, timedelta


Item = Mapping[str, Any]


def _item_datetime(item: Item) -> datetime:
    dt_str = item["properties"]["datetime"]
    # Planetary Computer returns ISO timestamps with "Z"
    return datetime.fromisoformat(dt_str.replace("Z", ""))


def select_snapshots_fractional(
    items: Sequence[Item],
    season_start: datetime,
    season_end: datetime,
    fractions: Sequence[float],
) -> List[Item]:
    """
    Select snapshots closest to given season fractions (e.g. [0.3, 0.7]).
    """
    if not items:
        return []

    items_sorted = sorted(items, key=_item_datetime)
    dur = (season_end - season_start).total_seconds()

    chosen: List[Item] = []
    used_idxs = set()

    for f in fractions:
        f = float(max(0.0, min(1.0, f)))
        target_dt = season_start + timedelta(seconds=f * dur)

        best_idx = None
        best_dt_diff = None
        for i, it in enumerate(items_sorted):
            dt = _item_datetime(it)
            diff = abs((dt - target_dt).total_seconds())
            if best_dt_diff is None or diff < best_dt_diff:
                best_dt_diff = diff
                best_idx = i

        if best_idx is not None and best_idx not in used_idxs:
            used_idxs.add(best_idx)
            chosen.append(items_sorted[best_idx])

    return chosen


def select_snapshot_fixed_date(items: Sequence[Item], target_dt: datetime) -> Item | None:
    """
    Single snapshot closest to a fixed target date.
    """
    if not items:
        return None

    items_sorted = sorted(items, key=_item_datetime)
    best_it = None
    best_diff = None
    for it in items_sorted:
        dt = _item_datetime(it)
        diff = abs((dt - target_dt).total_seconds())
        if best_diff is None or diff < best_diff:
            best_diff = diff
            best_it = it
    return best_it


def select_top_n_cloudfree(items: Sequence[Item], n: int) -> List[Item]:
    """
    Select N items with lowest cloud cover (eo:cloud_cover property if present).
    """
    if not items or n <= 0:
        return []
    items_sorted = sorted(
        items,
        key=lambda it: it["properties"].get("eo:cloud_cover", 0.0),
    )
    return items_sorted[:n]


def select_snapshots_all(items: Sequence[Item]) -> List[Item]:
    """
    Strategy 'all': use all items in the search window.
    """
    return list(items)


def select_snapshots_by_dates(
    items: Sequence[Item],
    dates: Sequence[datetime],
) -> List[Item]:
    """
    Strategy 'dates': select snapshots closest to a few key dates.
    """
    if not items or not dates:
        return []

    items_sorted = sorted(items, key=_item_datetime)
    chosen: List[Item] = []
    used_idxs = set()

    for target_dt in dates:
        best_idx = None
        best_diff = None
        for i, it in enumerate(items_sorted):
            dt = _item_datetime(it)
            diff = abs((dt - target_dt).total_seconds())
            if best_diff is None or diff < best_diff:
                best_diff = diff
                best_idx = i
        if best_idx is not None and best_idx not in used_idxs:
            used_idxs.add(best_idx)
            chosen.append(items_sorted[best_idx])

    return chosen
