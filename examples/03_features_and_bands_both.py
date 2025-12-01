import geopandas as gpd
from shapely.geometry import Point
from agrs.client import s2agc

field_geom = Point(-8.0, 32.0)

fields = gpd.GeoDataFrame(
    {"field_id": [1], "geometry": [field_geom]},
    crs="EPSG:4326",
)

client = s2agc(
    source="planetary_computer",
    max_cloud=0.2,
)

features_df, bands_df = client.get_features(
    fields=fields,
    field_id_col="field_id",
    start_date="2018-10-01",
    end_date="2019-06-30",
    crop="wheat",
    snapshot_strategy="fractional",
    fractions=[0.3, 0.6, 0.9, 1.0],
    return_mode="both",   # <- tuple (features_df, bands_df)
)

print("Features:")
print(features_df.head())
print("\nBand stats:")
print(bands_df.head())
