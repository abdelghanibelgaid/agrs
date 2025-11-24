# AGRS – Agricultural Remote Sensing Library (MVP)

## Description

AGRS is a domain-focused Python library that turns **Sentinel-2 imagery** into **agronomy-ready features** for various agricultural modeling tasks, such as yield modeling, stress analysis, and NPK recommendation.

Instead of dealing with STAC queries, cloud masks, band math, and geometry clipping in every project, AGRS provides **opinionated, agriculture-centric pipelines**:

- Search & fetch Sentinel-2 scenes (via Microsoft Planetary Computer STAC).
- Compute standard indices (NDVI, EVI, SAVI, NDWI, NDMI, GCI, NDRE, RECI, NBR, NBR2).
- Select snapshots using agronomic strategies (fractions of season, specific dates, best cloud-free scenes).
- Aggregate to field-level features per index and **growth stage** (early/mid/late season) with statistics (mean, median, min, max, std and more).
- Return a tidy `DataFrame` ready to join with yield, NPK, and management tables.

The goal is to maximize value for agricultural ML workflows: **field trial analysis**, **site-specific NPK optimization**, and **crop monitoring**.

## Key features

- Sentinel-2 access via **Planetary Computer STAC API**.
- Automatic band selection (default: all available bands) or user-defined.
- Built-in index formulas:
  - NDVI, EVI, SAVI, NDWI, NDMI, GCI, NDRE, RECI, NBR, NBR2
  - Robust handling of missing bands and divide-by-zero (graceful skip + warnings).
- Snapshot selection strategies:
  - `fractional` – e.g., snapshots near 30%, 60%, 90% of the season.
  - `fixed_date` – snapshot closest to a given date.
  - `top_n_cloudfree` – N lowest-cloud scenes in the period.
- Field-level aggregation:
  - For each index and stage: `mean`, `median`, `min`, `max`, `std`.
  - Early, mid, late stages defined as 0–33%, 33–66%, 66–100% of season duration.

## Quick example

```python
import geopandas as gpd
from shapely.geometry import Point
from agrs.client import s2agc

field_geom = Point(-8.0, 32.0)

fields = gpd.GeoDataFrame(
    {
        "field_id": [1],
        "geometry": [field_geom],
    },
    crs="EPSG:4326",
)

client = s2agc(
    source="planetary_computer",
    max_cloud=0.2,
)

features_df = client.get_features(
    fields=fields,
    field_id_col="field_id",
    start_date="2018-10-01",
    end_date="2019-06-30",
    crop="wheat",
    n_snapshots=4,
    snapshot_strategy="fractional",
    fractions=[0.3, 0.6, 0.9, 1.0],
)

print(features_df.head())
