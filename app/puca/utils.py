import requests
import logging
from typing import List, Optional
import math
import sys
import config
from puca.models import Coordinates, BoundingBox, LoggerConfig
import overpy
from geopy.distance import geodesic
from geopy.point import Point
import os
import json



def setup_logger(config: Optional[LoggerConfig] = None) -> logging.Logger:
    """Set up and return a configured logger"""
    if config is None:
        config = LoggerConfig(
            level="INFO",
            output="stdout"
        )
    logger = logging.getLogger(config.name)
    
    # Check if logger already has handlers to avoid duplicate logs
    if logger.handlers:
        return logger
        
    # Set log level - fix the level string
    log_level_str = config.level.upper()  # Ensure uppercase
    if hasattr(logging, log_level_str):
        logger.setLevel(getattr(logging, log_level_str))
    else:
        # Fallback to INFO if the level is invalid
        logger.setLevel(logging.INFO)
        logger.warning(f"Invalid log level: {config.level}, using INFO instead")
    
    # Create handler
    if config.output == "stdout":
        handler = logging.StreamHandler(sys.stdout)
    else:
        handler = logging.FileHandler(config.output)
    
    # Set formatter
    formatter = logging.Formatter(config.format)
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger

logger = setup_logger(config)

def query_overpass(query, bounding_box: BoundingBox) -> str:
    """
    Queries the Overpass API
    """
    query_template = f"""
    [out:json];
    (
    {query} ({bounding_box.bottom_right_lat}, {bounding_box.top_left_lon}, {bounding_box.top_left_lat}, {bounding_box.bottom_right_lon});
    );
    out body;
    """
    overpass = overpy.Overpass()
    result = overpass.query(query_template)
    return result

def get_building_name(lat: float, lon: float) -> str:
    """
    Queries the Overpass API to get the nearest building and returns the name of the building
    """
    query_template = f"""
    [out:json][timeout:25];
    way(around:10, {lat}, {lon})["building"]["name"];
    out center;
    """
    overpass = overpy.Overpass()
    result = overpass.query(query_template)
    for way in result.ways:
        logger.debug(f"overpass result: {way}")
        name = way.tags.get("name", "")
        return name


def get_distance_between_points(lat1: float, lon1: float, lat2: float, lon2: float) -> str:
    url = f"{config.OSRM_BASE_URL}/{lon1},{lat1};{lon2},{lat2}?overview=false"
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text) 
        distance = data['routes'][0]['distance']  # Distance in meters
        return distance
    else:
        return "Unknown"

# def query_overpass(lat: float, lon: float, query: str) -> Optional[List[str]]:
#     """
#     A generic function to query the Overpass API with a custom Overpass query.
#     """
#     # Create the Overpass API query
#     overpass_query = f"""
#     [out:json];
#     area[name="Newry"][place="city"];
#     node[amenity="toilets"](area);
#     out;
#     """
#     # Send the request to the Overpass API
#     response = requests.get(config.OVERPASS_BASE_URL, params={'data': overpass_query})
    
#     if response.status_code == 200:
#         data = response.json()
#         # Extract results based on the query
#         results = []
#         for element in data.get("elements", []):
#             if "tags" in element:
#                 results.append(element["tags"].get("name", "Unnamed"))
#         return results
#     return None


def get_bounding_box(lat: float, lon: float, distance: float) -> Optional[BoundingBox]:
  
    center_point = Point(lat, lon)
    # Calculate the distance offset in degrees for the specified distance in meters
    # Roughly 1 degree of latitude is 111,000 meters
    lat_offset = distance / 111000.0
    # Longitude offset: 1 degree of longitude is roughly 111,000 meters at the equator
    # At different latitudes, the length of a degree of longitude changes.
    lon_offset = distance / (111000.0 * abs(math.cos(math.radians(lat))))

    # Calculate the top-left and bottom-right corners of the bounding box
    top_left = Point(lat + lat_offset, lon - lon_offset)
    bottom_right = Point(lat - lat_offset, lon + lon_offset)

    return BoundingBox(
        top_left_lat = top_left.latitude, 
        top_left_lon = top_left.longitude, 
        bottom_right_lat = bottom_right.latitude, 
        bottom_right_lon = bottom_right.longitude
    )


def get_bounds_by_address(address: str, distance: int) -> Optional[BoundingBox]:
    coords = get_address_coordinates(address)
    return_text = ""
    if coords:
        return_text += f"Latitude: {coords.lat}, Longitude: {coords.lon}"
    else:
        return_text += "Address not found"
    bounding_box = get_bounding_box(coords.lat, coords.lon, distance)
    return bounding_box


def get_address_coordinates(address: str) -> Optional[Coordinates]:
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "MCP-Server/1.0 (jonny.mccullagh@gmail.com)"
    }
    response = requests.get(config.NOMINATIM_BASE_URL + '/search', params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data:
            return Coordinates(lat=float(data[0]["lat"]), lon=float(data[0]["lon"]))
    
    return None

def get_address_from_coordinates(lat: float, lon: float) -> Optional[str]:
    
    params = {
        "lat": lat,
        "lon": lon,
        "extratags": 1,
        "format": "json"
    }
    headers = {
        "User-Agent": "Puca-Mcp-Server/1.0 (jonny.mccullagh@gmail.com)"  # Replace with your app name and contact
    }
    response = requests.get(config.NOMINATIM_BASE_URL + '/reverse', params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        logger.debug(f"Reverse address lookup returned: {data}")
        if "display_name" in data:
            return data["display_name"]  # This returns a human-readable address
    return None

def validate_coordinates(lat, lon):
    try:
        # Convert to floats
        lat = float(lat)
        lon = float(lon)
        
        # Validate latitude and longitude ranges
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            return True
        else:
            return False
    except (ValueError, TypeError):
        # Invalid format (e.g., cannot convert to float)
        return False
    
