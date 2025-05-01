"""
Functions to return info about OpenStreetMap resources tagged with 'leisure'
"""

from typing import List, Optional
from puca.models import BoundingBox
from puca.utils import query_overpass


def pitch(bounding_box: BoundingBox) -> Optional[List[str]]:
    """
    Queries the Overpass API to get a list of leisure pitches based on coordinates.
    """
    result = query_overpass(query='nwr["leisure"="pitch"]', bounding_box=bounding_box)
    return result


def fitness_centre(bounding_box: BoundingBox) -> Optional[List[str]]:
    """
    Queries the Overpass API to get a list of gyms based on coordinates.
    """
    result = query_overpass(
        query='nwr["leisure"="fitness_centre"]', bounding_box=bounding_box
    )
    return result
