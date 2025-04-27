import config
from typing import List, Optional
from puca.models import Coordinates, BoundingBox
from puca.utils import query_overpass


def hotel(bounding_box: BoundingBox) -> Optional[List[str]]:
    """
    Queries the Overpass API to get a list of hotels based on coordinates.
    """
    result = query_overpass(query = 'nwr["tourism"="hotel"]', bounding_box = bounding_box)
    return result

def museum(bounding_box: BoundingBox) -> Optional[List[str]]:
    """
    Queries the Overpass API to get a list of museums based on coordinates.
    """
    result = query_overpass(query = 'nwr["tourism"="museum"]', bounding_box = bounding_box)
    return result

