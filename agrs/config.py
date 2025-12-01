DEFAULT_INDICES = [
    "NDVI",     # Normalized Difference Vegetation Index
    "EVI",      # Enhanced Vegetation Index
    "EVI2",     # Two-band EVI
    "SAVI",     # Soil-Adjusted Vegetation Index
    "MSAVI",    # Modified SAVI
    "OSAVI",    # Optimized SAVI
    "GNDVI",    # Green NDVI
    "VARI",     # Visible Atmospherically Resistant Index
    "GCI",      # Green Chlorophyll Index
    "NDRE",     # Red Edge NDVI
    "RECI",     # Red Edge Chlorophyll Index
    "ARVI",     # Atmospherically Resistant Vegetation Index
    "MCARI",    # Modified Chlorophyll Absorption Ratio Index
    "MCARI2",   # MCARI2 variant
    "NDWI",     # McFeeters NDWI (Green/NIR)
    "MNDWI",    # Modified NDWI (Green/SWIR1)
    "NDMI",     # Normalized Difference Moisture Index (NIR/SWIR1)
    "NBR",      # Normalized Burn Ratio (NIR/SWIR2)
    "NBR2",     # Normalized Burn Ratio 2 (SWIR1/SWIR2)
]

DEFAULT_SUMMARY_STATS = ["mean", "median", "min", "max", "std"]

# Default snapshot fractions for "fractional" strategy.
DEFAULT_FRACTIONS = [0.25, 0.5, 0.75]

# Early, mid, late as fractions of season duration
DEFAULT_STAGE_BOUNDS = {
    "early":  (0.0, 0.33),
    "mid":    (0.33, 0.66),
    "late":   (0.66, 1.01),
}
