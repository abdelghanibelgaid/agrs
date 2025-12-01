from typing import Dict
import numpy as np

def _safe_divide(num: np.ndarray, den: np.ndarray) -> np.ndarray:
    """Elementwise division with NaN on invalid/zero."""
    with np.errstate(divide="ignore", invalid="ignore"):
        out = np.true_divide(num, den)
        out[~np.isfinite(out)] = np.nan
    return out

def compute_indices(bands: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    """
    Compute a suite of classic RS indices from Sentinel-2 bands.

    Parameters
    ----------
    bands : dict
        Mapping band_code -> array (e.g. "B02", "B03", ..., "B12").

    Returns
    -------
    dict
        Mapping index_name -> array. Only indices whose required
        bands are present are returned.
    """
    out: Dict[str, np.ndarray] = {}

    B01 = bands.get("B01")  # Aerosol / coastal
    B02 = bands.get("B02")  # Blue
    B03 = bands.get("B03")  # Green
    B04 = bands.get("B04")  # Red
    B05 = bands.get("B05")  # RE1
    B06 = bands.get("B06")  # RE2
    B07 = bands.get("B07")  # RE3
    B08 = bands.get("B08")  # NIR
    B8A = bands.get("B8A")  # Narrow NIR
    B11 = bands.get("B11")  # SWIR1
    B12 = bands.get("B12")  # SWIR2

    # Helper: choose best NIR variant available
    NIR = B08 if B08 is not None else (B8A if B8A is not None else None)

    # --- Vegetation indices ---

    # NDVI = (NIR - Red) / (NIR + Red)
    if NIR is not None and B04 is not None:
        out["NDVI"] = _safe_divide(NIR - B04, NIR + B04)

    # EVI (3-band version) (Huete 2002)
    # EVI = 2.5 * (NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1)
    if NIR is not None and B04 is not None and B02 is not None:
        out["EVI"] = _safe_divide(
            2.5 * (NIR - B04),
            (NIR + 6.0 * B04 - 7.5 * B02 + 1.0),
        )

    # EVI2 (2-band version, Jiang 2008)
    # EVI2 = 2.5 * (NIR - Red) / (NIR + 2.4*Red + 1)
    if NIR is not None and B04 is not None:
        out["EVI2"] = _safe_divide(
            2.5 * (NIR - B04),
            (NIR + 2.4 * B04 + 1.0),
        )

    # SAVI (L=0.5)
    # SAVI = (1 + L) * (NIR - Red) / (NIR + Red + L)
    if NIR is not None and B04 is not None:
        L = 0.5
        out["SAVI"] = _safe_divide(
            (1.0 + L) * (NIR - B04),
            (NIR + B04 + L),
        )

    # MSAVI (Qi 1994)
    if NIR is not None and B04 is not None:
        out["MSAVI"] = 0.5 * (
            2.0 * NIR + 1.0 - np.sqrt((2.0 * NIR + 1.0) ** 2 - 8.0 * (NIR - B04))
        )

    # OSAVI (Rondeaux 1996), L=0.16
    if NIR is not None and B04 is not None:
        L = 0.16
        out["OSAVI"] = _safe_divide(
            (NIR - B04),
            (NIR + B04 + L),
        )

    # GNDVI = (NIR - Green) / (NIR + Green)
    if NIR is not None and B03 is not None:
        out["GNDVI"] = _safe_divide(NIR - B03, NIR + B03)

    # VARI = (Green - Red) / (Green + Red - Blue)
    if B03 is not None and B04 is not None and B02 is not None:
        out["VARI"] = _safe_divide(
            B03 - B04,
            B03 + B04 - B02,
        )

    # GCI = (NIR / Green) - 1
    if NIR is not None and B03 is not None:
        out["GCI"] = _safe_divide(NIR, B03) - 1.0

    # NDRE = (NIR - RE) / (NIR + RE) (use B08/B8A and B05/B06/B07)
    RE = B05 if B05 is not None else (B06 if B06 is not None else B07)
    if NIR is not None and RE is not None:
        out["NDRE"] = _safe_divide(NIR - RE, NIR + RE)

    # RECI = (NIR / RE) - 1
    if NIR is not None and RE is not None:
        out["RECI"] = _safe_divide(NIR, RE) - 1.0

    # ARVI = (NIR - (2*Red - Blue)) / (NIR + (2*Red - Blue))
    if NIR is not None and B04 is not None and B02 is not None:
        rb = 2.0 * B04 - B02
        out["ARVI"] = _safe_divide(NIR - rb, NIR + rb)

    # MCARI (Daughtry 2000)
    # MCARI = ((RE - Red) - 0.2*(RE - Green)) * (RE / Red)
    if RE is not None and B04 is not None and B03 is not None:
        mcari_num = (RE - B04) - 0.2 * (RE - B03)
        out["MCARI"] = mcari_num * _safe_divide(RE, B04)

    # MCARI2 (Haboudane 2004)
    if "MCARI" in out and "OSAVI" in out:
        out["MCARI2"] = out["MCARI"] * _safe_divide(out["OSAVI"], out["OSAVI"] + 0.08)

    # --- Water / moisture / burn indices ---

    # NDWI (McFeeters) = (Green - NIR) / (Green + NIR)
    if NIR is not None and B03 is not None:
        out["NDWI"] = _safe_divide(B03 - NIR, B03 + NIR)

    # MNDWI (Xu) = (Green - SWIR1) / (Green + SWIR1)
    if B03 is not None and B11 is not None:
        out["MNDWI"] = _safe_divide(B03 - B11, B03 + B11)

    # NDMI (a.k.a. NDWI-Gao) = (NIR - SWIR1) / (NIR + SWIR1)
    if NIR is not None and B11 is not None:
        out["NDMI"] = _safe_divide(NIR - B11, NIR + B11)

    # NBR  = (NIR - SWIR2) / (NIR + SWIR2)
    if NIR is not None and B12 is not None:
        out["NBR"] = _safe_divide(NIR - B12, NIR + B12)

    # NBR2 = (SWIR1 - SWIR2) / (SWIR1 + SWIR2)
    if B11 is not None and B12 is not None:
        out["NBR2"] = _safe_divide(B11 - B12, B11 + B12)

    return out
