from typing import Tuple, Dict
from shapely.geometry import mapping
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from rasterio.warp import transform_geom
import numpy as np



def gdf_to_bbox(gdf: gpd.GeoDataFrame) -> Tuple[float, float, float, float]:
    bounds = gdf.total_bounds  # minx, miny, maxx, maxy
    return tuple(bounds.tolist())



def clip_raster_to_geom(
    asset_href: str,
    geom,
    bands: Dict[str, str],
) -> Dict[str, np.ndarray]:
    """
    geom: shapely geometry in EPSG:4326 (WGS84).
    bands: mapping band_code -> href
    Returns: dict band_code -> clipped array.
    If geometry does not overlap the raster, returns {}.
    """
    out = {}



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
                # Shapes do not overlap raster: skip this band (and effectively this item)
                if "do not overlap raster" in str(e):
                    return {}  # no overlap for this item; caller will skip it
                else:
                    raise



            # arr shape: (1, H, W)
            out[band_code] = arr[0].astype("float32")



    return out
