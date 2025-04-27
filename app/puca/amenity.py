import config
from typing import List, Optional
from puca.models import Coordinates, BoundingBox
from puca.utils import query_overpass


def get_amenity(type: str, bounding_box: BoundingBox) -> Optional[List[str]]:
    """
    Queries the Overpass API to get a list of parking locations based on coordinates.
    """
    if type == "parking":
        query_string = 'nwr["amenity"="parking"]'
    elif type == "toilets":
        query_string = 'nwr["amenity"="toilets"]'
    elif type == "community_centre":
        query_string = 'nwr["amenity"="community_centre"]'
    elif type == "post_office":
        query_string = 'nwr["amenity"="post_office"]'
    elif type == "cafe":
        query_string = 'nwr["amenity"="cafe"]'
    elif type == "fast_food":
        query_string = 'nwr["amenity"="fast_food"]'
    else:
        return f"Amenity {type} is not valid."

    result = query_overpass(query = query_string, bounding_box = bounding_box)
    return result
