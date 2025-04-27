import config
from typing import List, Optional
from puca.models import Coordinates, BoundingBox
from puca.utils import query_overpass


def irish_street_names(bounding_box: BoundingBox) -> Optional[List[str]]:
    """
    Queries the Overpass API to get a list of schools based on coordinates.
    """
    result = query_overpass(query = 'way["name:ga"]', bounding_box = bounding_box)
    return result
