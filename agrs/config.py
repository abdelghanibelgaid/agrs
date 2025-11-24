DEFAULT_INDICES = [
    "NDVI",
    "EVI",
    "SAVI",
    "NDWI",
    "NDMI",
    "GCI",
    "NDRE",
    "RECI",
    "NBR",
    "NBR2",
]

DEFAULT_SUMMARY_STATS = ["mean", "median", "min", "max", "std"]

# Early, mid, late as fractions of season duration
DEFAULT_STAGE_BOUNDS = {
    "early":  (0.0, 0.33),
    "mid":    (0.33, 0.66),
    "late":   (0.66, 1.01),
}
