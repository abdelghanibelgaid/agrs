import numpy as np
import logging
from typing import Dict

logger = logging.getLogger(__name__)

# Helper to safely divide
def _safe_div(numer, denom, eps=1e-6):
    denom_safe = np.where(np.abs(denom) < eps, np.nan, denom)
    return np.divide(numer, denom_safe)

def compute_indices(bands: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    """
    Compute all supported indices from a dict of bands.
    bands: mapping like {"B02": arr, "B03": arr, ...}
    Returns dict of index_name -> array (same shape).
    Skips indices if required bands missing; logs warning.
    """
    idx = {}

    def has(*needed):
        miss = [b for b in needed if b not in bands]
        if miss:
            logger.warning("Missing bands %s for index, skipping.", miss)
            return False
        return True

    # NDVI: (NIR - RED) / (NIR + RED) = (B08 - B04) / (B08 + B04)
    if has("B08", "B04"):
        num = bands["B08"] - bands["B04"]
        den = bands["B08"] + bands["B04"]
        idx["NDVI"] = _safe_div(num, den)

    # EVI: 2.5 * (NIR - RED) / (NIR + 6*RED - 7.5*BLUE + 1)
    if has("B08", "B04", "B02"):
        num = bands["B08"] - bands["B04"]
        den = bands["B08"] + 6.0 * bands["B04"] - 7.5 * bands["B02"] + 1.0
        idx["EVI"] = 2.5 * _safe_div(num, den)

    # SAVI: (NIR - RED) / (NIR + RED + L) * (1 + L), L=0.5
    if has("B08", "B04"):
        L = 0.5
        num = bands["B08"] - bands["B04"]
        den = bands["B08"] + bands["B04"] + L
        idx["SAVI"] = (1 + L) * _safe_div(num, den)

    # NDWI (Gao): (NIR - SWIR) / (NIR + SWIR) = (B08 - B11) / (B08 + B11)
    if has("B08", "B11"):
        num = bands["B08"] - bands["B11"]
        den = bands["B08"] + bands["B11"]
        idx["NDWI"] = _safe_div(num, den)

    # NDMI: (NIR - SWIR2) / (NIR + SWIR2) = (B08 - B12) / (B08 + B12)
    if has("B08", "B12"):
        num = bands["B08"] - bands["B12"]
        den = bands["B08"] + bands["B12"]
        idx["NDMI"] = _safe_div(num, den)

    # GCI: (NIR / GREEN) - 1 = (B08 / B03) - 1
    if has("B08", "B03"):
        idx["GCI"] = _safe_div(bands["B08"], bands["B03"]) - 1.0

    # NDRE: (NIR - RE1) / (NIR + RE1) = (B08 - B05) / (B08 + B05)
    if has("B08", "B05"):
        num = bands["B08"] - bands["B05"]
        den = bands["B08"] + bands["B05"]
        idx["NDRE"] = _safe_div(num, den)

    # RECI: (NIR / RE1) - 1 = (B08 / B05) - 1
    if has("B08", "B05"):
        idx["RECI"] = _safe_div(bands["B08"], bands["B05"]) - 1.0

    # NBR: (NIR - SWIR2) / (NIR + SWIR2) = (B08 - B12) / (B08 + B12)
    if has("B08", "B12"):
        num = bands["B08"] - bands["B12"]
        den = bands["B08"] + bands["B12"]
        idx["NBR"] = _safe_div(num, den)

    # NBR2: (SWIR1 - SWIR2) / (SWIR1 + SWIR2) = (B11 - B12) / (B11 + B12)
    if has("B11", "B12"):
        num = bands["B11"] - bands["B12"]
        den = bands["B11"] + bands["B12"]
        idx["NBR2"] = _safe_div(num, den)

    return idx
