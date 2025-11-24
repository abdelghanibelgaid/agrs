from typing import List, Dict, Any, Optional
from datetime import datetime
import logging



import pystac_client
import planetary_computer



logger = logging.getLogger(__name__)



S2_L2A_COLLECTION = "sentinel-2-l2a"



class PlanetaryComputerS2Source:
    """
    Sentinel-2 data source using Microsoft Planetary Computer STAC.
    """



    def __init__(
        self,
        max_cloud: float = 0.3,
        stac_url: str = "https://planetarycomputer.microsoft.com/api/stac/v1",
    ):
        self.max_cloud = max_cloud
        self.client = pystac_client.Client.open(
            stac_url,
            modifier=planetary_computer.sign_inplace,
        )



    def search_items(
        self,
        bbox: List[float],
        start_date: str,
        end_date: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        bbox: [minx, miny, maxx, maxy]
        Returns list of STAC items (as dicts).
        """
        search = self.client.search(
            collections=[S2_L2A_COLLECTION],
            bbox=bbox,
            datetime=f"{start_date}/{end_date}",
            max_items=limit,
            query={"eo:cloud_cover": {"lt": self.max_cloud * 100}},
        )
        items = list(search.get_items())
        logger.info("Found %d items in STAC search.", len(items))
        # convert to plain dicts to be consistent with selection helpers
        return [item.to_dict() for item in items]
