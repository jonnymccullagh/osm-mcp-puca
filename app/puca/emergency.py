"""
Functions to return info about OpenStreetMap resources tagged with 'emergency'
"""

from typing import List, Optional
from puca.models import BoundingBox
from puca.utils import query_overpass


def defibrillators(bounding_box: BoundingBox) -> Optional[List[str]]:
    """
    Queries the Overpass API to get a list of defibrillator locations based on coordinates.
    """
    result = query_overpass(
        query='node["emergency"="defibrillator"]', bounding_box=bounding_box
    )
    return result
