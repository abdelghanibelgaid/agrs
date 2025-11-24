from typing import List, Dict, Any, Tuple
from datetime import datetime

import planetary_computer as pc
from pystac_client import Client


class PlanetaryComputerS2Source:
    """
    Minimal Sentinel-2 L2A source backed by Microsoft Planetary Computer.

    Parameters
    ----------
    max_cloud : float
        Maximum allowed cloud cover fraction in [0, 1]. This is converted to
        percentage for the STAC query (eo:cloud_cover < max_cloud * 100).
    """

    def __init__(self, max_cloud: float = 0.3) -> None:
        self.max_cloud = float(max_cloud)
        self._client = Client.open(
            "https://planetarycomputer.microsoft.com/api/stac/v1",
            modifier=pc.sign_inplace,
        )

    def search_items(
        self,
        bbox: Tuple[float, float, float, float],
        start_date: str,
        end_date: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Search Sentinel-2 L2A items in Planetary Computer.

        Returns a list of pystac Items converted to plain dicts.
        """
        datetime_range = f"{start_date}/{end_date}"

        search = self._client.search(
            collections=["sentinel-2-l2a"],
            bbox=bbox,
            datetime=datetime_range,
            max_items=limit,
            query={
                "eo:cloud_cover": {
                    "lt": self.max_cloud * 100.0
                }
            },
        )

        items = list(search.get_items())
        return [item.to_dict() for item in items]
