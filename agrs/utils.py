from typing import Tuple, Dict

from shapely.geometry import mapping
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from rasterio.warp import transform_geom
import numpy as np


def gdf_to_bbox(gdf: gpd.GeoDataFrame) -> Tuple[float, float, float, float]:
    """
    Convert a GeoDataFrame to a bounding box tuple (minx, miny, maxx, maxy).
    """
    bounds = gdf.total_bounds  # minx, miny, maxx, maxy
    return tuple(bounds.tolist())


def clip_raster_to_geom(
    asset_href: str,
    geom,
    bands: Dict[str, str],
) -> Dict[str, np.ndarray]:
    """
    Clip raster bands to a geometry.

    Parameters
    ----------
    asset_href : str
        Unused in this MVP; kept for potential future extension.
    geom : shapely geometry
        Geometry in EPSG:4326 (WGS84).
    bands : dict
        Mapping band_code -> href for each band.

    Returns
    -------
    dict
        Mapping band_code -> clipped numpy array (H, W).
        If geometry does not overlap any band raster, returns {}.
    """
    out: Dict[str, np.ndarray] = {}

    for band_code, href in bands.items():
        with rasterio.open(href) as src:
            # Reproject geometry from EPSG:4326 to raster CRS if needed
            geom_geojson = [mapping(geom)]
            if src.crs is not None and src.crs.to_string() != "EPSG:4326":
                geom_geojson = [
                    transform_geom("EPSG:4326", src.crs, g) for g in geom_geojson
                ]

            try:
                arr, _ = mask(src, geom_geojson, crop=True)
            except ValueError as e:
                # Shapes do not overlap raster: skip this item entirely
                if "do not overlap raster" in str(e):
                    return {}
                else:
                    raise

            # arr shape: (1, H, W)
            out[band_code] = arr[0].astype("float32")

    return out
