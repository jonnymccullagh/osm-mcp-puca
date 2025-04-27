import config
from typing import List, Optional
from puca.models import Coordinates, BoundingBox
from puca.utils import query_overpass


def school(bounding_box: BoundingBox) -> Optional[List[str]]:
    """
    Queries the Overpass API to get a list of schools based on coordinates.
    """
    result = query_overpass(query = 'nwr["building"="school"]', bounding_box = bounding_box)
    return result


def kindergarten(bounding_box: BoundingBox) -> Optional[List[str]]:
    """
    Queries the Overpass API to get a list of kindergartens based on coordinates.
    """
    result = query_overpass(query = 'nwr["building"="kindergarten"]', bounding_box = bounding_box)
    return result


def retail(bounding_box: BoundingBox) -> Optional[List[str]]:
    """
    Queries the Overpass API to get a list of gyms based on coordinates.
    """
    result = query_overpass(query = 'nwr["building"="retail"]', bounding_box = bounding_box)
    return result
