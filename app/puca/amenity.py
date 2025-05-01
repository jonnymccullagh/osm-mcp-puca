"""
Functions to return info about OpenStreetMap resources tagged with 'amenity'
"""

from typing import List, Optional
from puca.models import BoundingBox
from puca.utils import query_overpass


def get_amenity(amenity: str, bounding_box: BoundingBox) -> Optional[List[str]]:
    """
    Queries the Overpass API to get a list of parking locations based on coordinates.
    """
    if amenity == "parking":
        query_string = 'nwr["amenity"="parking"]'
    elif amenity == "toilets":
        query_string = 'nwr["amenity"="toilets"]'
    elif amenity == "community_centre":
        query_string = 'nwr["amenity"="community_centre"]'
    elif amenity == "post_office":
        query_string = 'nwr["amenity"="post_office"]'
    elif amenity == "cafe":
        query_string = 'nwr["amenity"="cafe"]'
    elif amenity == "fast_food":
        query_string = 'nwr["amenity"="fast_food"]'
    else:
        return f"Amenity {amenity} is not valid."

    result = query_overpass(query=query_string, bounding_box=bounding_box)
    return result
