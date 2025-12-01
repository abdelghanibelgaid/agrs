# AGRS – Agricultural Remote Sensing Library

<p align="center">
  <!-- PyPI version -->
  <a href="https://pypi.org/project/agrs/">
    <img src="https://img.shields.io/pypi/v/agrs.svg?label=PyPI" alt="PyPI" />
  </a>

  <!-- DOI -->
  <a href="https://doi.org/10.5281/zenodo.17699363">
    <img src="https://zenodo.org/badge/DOI/10.5281/zenodo.17699363.svg" alt="DOI" />
  </a>

  <!-- Security -->
  <a href="https://socket.dev/pypi/package/agrs">
    <img src="https://badge.socket.dev/pypi/package/agrs/0.1.3?artifact_id=tar-gz#1764083045680" alt="Socket" />
  </a>

  <!-- Downloads -->
  <a href="https://pepy.tech/project/agrs">
    <img src="https://static.pepy.tech/badge/agrs" alt="Downloads" />
  </a>

  <!-- License -->
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT" />
  </a>
</p>

## Description

AGRS is a domain-focused Python library that turns **Sentinel-2 imagery** into **agronomy-ready features** for tasks such as yield modeling, stress analysis, and site-specific fertilizer (NPK) recommendation.

Instead of re-implementing STAC queries, cloud filters, band math, and geometry clipping in every project, AGRS provides **opinionated, agriculture-centric pipelines**:

- Search & fetch Sentinel-2 L2A scenes (via Microsoft Planetary Computer STAC).
- Compute a comprehensive set of classic vegetation, water, moisture, and burn indices.
- Select snapshots using agronomic strategies (fractions of season, specific dates, all scenes, best cloud-free scenes).
- Aggregate to **field-level features** per index and time-fraction of the season.
- Optionally return **per-band statistics** (mean, median, percentiles, …) for QA and custom modeling.
- Return tidy `pandas.DataFrame` objects ready to join with yield, NPK, and management tables.

The goal is to maximize value for agricultural ML workflows: **field trial analysis**, **site-specific NPK optimization**, and **crop monitoring**.

## Key features

- **Sentinel-2 access**
  - Microsoft Planetary Computer STAC API.
  - Automatic bounding-box search from field geometries (`GeoDataFrame`).

- **Band handling**
  - Automatic band detection (default: all `B*` assets) or user-defined band list.
  - Robust geometry clipping for each field.

- **Built-in index formulas (Sentinel-2 friendly)**  
  (only computed if required bands are present)
  - Vegetation / chlorophyll:
    - `NDVI`, `EVI`, `EVI2`, `SAVI`, `MSAVI`, `OSAVI`
    - `GNDVI`, `VARI`, `GCI`
    - `NDRE`, `RECI`, `ARVI`
    - `MCARI`, `MCARI2`
  - Water / moisture / burn:
    - `NDWI` (McFeeters), `MNDWI`
    - `NDMI` (a.k.a moisture index)
    - `NBR`, `NBR2`
  - Safe division with NaNs for invalid cases (no hard crashes on zero / missing).

- **Snapshot selection strategies**
  - `fractional` – nearest scenes to temporal fractions (e.g. `[0.3, 0.7]` of the season).
  - `fixed_date` – snapshot closest to a single target date.
  - `dates` – snapshots closest to a list of key dates.
  - `top_n_cloudfree` – N scenes with lowest `eo:cloud_cover`.
  - `all` – use all scenes between `start_date` and `end_date`.

- **Return modes**
  - `return_mode="features"` (default):
    - Field-level aggregated index features (per field, per index, per time-fraction).
  - `return_mode="bands"`:
    - Per-field, per-date statistics for each band:
      - `mean`, `median`, `min`, `max`, `std`, `p10`, `p90`.
  - `return_mode="both"`:
    - Tuple `(features_df, bands_df)` with both outputs.

- **Field-level aggregation**
  - For each field and index:
    - Aggregation over the selected snapshots with statistics such as `mean`, `median`, `min`, `max`, `std`.
  - Uses time fractions to encode position within the season (0–1).

## Installation

```bash
pip install agrs
````

AGRS requires Python 3.9+ and depends on `geopandas`, `shapely`, `rasterio`, `pystac-client`, and `planetary-computer`.

## Quick start (features only)

```python
import geopandas as gpd
from shapely.geometry import Point
from agrs.client import s2agc

# 1) Single test field
field_geom = Point(-8.0, 32.0)

fields = gpd.GeoDataFrame(
    {"field_id": [1], "geometry": [field_geom]},
    crs="EPSG:4326",
)

# 2) Create client
client = s2agc(
    source="planetary_computer",
    max_cloud=0.2,
)

# 3) Get field-level index features with fractional snapshots (e.g. 30%, 60%, 90%, 100% of season)
features_df = client.get_features(
    fields=fields,
    field_id_col="field_id",
    start_date="2018-10-01",
    end_date="2019-06-30",
    crop="wheat",
    snapshot_strategy="fractional",
    fractions=[0.3, 0.6, 0.9, 1.0],
    return_mode="features",  # default
)

print(features_df.head())
```

## Examples of other behaviours

### 1. Custom fractional snapshots (e.g. 30% and 70% of season)

```python
features_df = client.get_features(
    fields=fields,
    field_id_col="field_id",
    start_date="2018-10-01",
    end_date="2019-06-30",
    crop="wheat",
    snapshot_strategy="fractional",
    fractions=[0.3, 0.7],
    return_mode="features",
)
```

### 2. Bands only (all snapshots between two dates)

```python
bands_df = client.get_features(
    fields=fields,
    field_id_col="field_id",
    start_date="2018-10-01",
    end_date="2019-06-30",
    crop="wheat",
    snapshot_strategy="all",   # use all available scenes
    return_mode="bands",       # per-band stats per date
)

print(bands_df.head())
```

### 3. Features + bands together

```python
features_df, bands_df = client.get_features(
    fields=fields,
    field_id_col="field_id",
    start_date="2018-10-01",
    end_date="2019-06-30",
    crop="wheat",
    snapshot_strategy="dates",
    key_dates=["2019-02-15", "2019-04-01"],
    return_mode="both",
)
```

More usage patterns (fixed-date, top-N cloud-free, multi-field examples) are available in the `examples/` folder.

## Contributing

Contributions, bug reports, and feature requests are very welcome.

Please see **[CONTRIBUTING.md](CONTRIBUTING.md)** for guidelines on how to:

* Set up a development environment
* Run tests and examples
* Propose new indices, snapshot strategies, or data sources
* Open issues and pull requests

## License

AGRS is released under the **MIT License**. See [LICENSE](LICENSE) for details.
