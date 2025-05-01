"""Utility functions used throughout the puca files"""
import logging
import json
from typing import Optional
import math
import sys
import requests
import overpy
from geopy.point import Point
import config
from puca.models import Coordinates, BoundingBox, LoggerConfig
# from staticmap import StaticMap, CircleMarker


def setup_logger(config: Optional[LoggerConfig] = None) -> logging.Logger:
    """Set up and return a configured logger"""
    if config is None:
        config = LoggerConfig(level="INFO", output="stdout")
    logger = logging.getLogger(config.name)
    if logger.handlers:
        return logger
    log_level_str = config.level.upper()
    if hasattr(logging, log_level_str):
        logger.setLevel(getattr(logging, log_level_str))
    else:
        # Fallback to INFO if the level is invalid
        logger.setLevel(logging.INFO)
        logger.warning("Invalid log level: %s, using INFO instead", config.level)
    if config.output == "stdout":
        handler = logging.StreamHandler(sys.stdout)
    else:
        handler = logging.FileHandler(config.output)
    formatter = logging.Formatter(config.format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

logger = setup_logger(config)


def query_overpass(query, bounding_box: BoundingBox) -> str:
    """
    Queries the Overpass API
    """
    bottom_right_lat = bounding_box.bottom_right_lat
    top_left_lon = bounding_box.top_left_lon
    top_left_lat = bounding_box.top_left_lat
    bottom_right_lon = bounding_box.bottom_right_lon
    query_template = f"""
    [out:json];
    (
    {query} ({bottom_right_lat}, {top_left_lon}, {top_left_lat}, {bottom_right_lon});
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
        logger.debug("overpass result: %s", way)
        name = way.tags.get("name", "")
        return name

# def get_map_image(lat: float, lon: float):
#     m = StaticMap(400, 400, url_template="http://a.tile.osm.org/{z}/{x}/{y}.png")
#     marker = CircleMarker((lat, lon), "#0036FF", 12)
#     m.add_marker(marker)
#     image = m.render(zoom=18)
#     image.save("marker.png")


def get_distance_between_points(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> str:
    """Return the distance of a route between two coordinates"""
    url = f"{config.OSRM_BASE_URL}/{lon1},{lat1};{lon2},{lat2}?overview=false"
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)
        distance = data["routes"][0]["distance"]  # Distance in meters
        return distance
    return "Unknown"


def get_bounding_box(lat: float, lon: float, distance: float) -> Optional[BoundingBox]:
    """Use a latitude and longitude to create a box for overpass queries"""
    lat_offset = distance / 111000.0
    lon_offset = distance / (111000.0 * abs(math.cos(math.radians(lat))))

    # Calculate the top-left and bottom-right corners of the bounding box
    top_left = Point(lat + lat_offset, lon - lon_offset)
    bottom_right = Point(lat - lat_offset, lon + lon_offset)

    return BoundingBox(
        top_left_lat=top_left.latitude,
        top_left_lon=top_left.longitude,
        bottom_right_lat=bottom_right.latitude,
        bottom_right_lon=bottom_right.longitude,
    )


def get_bounds_by_address(address: str, distance: int) -> Optional[BoundingBox]:
    """Use a an address to create a box for overpass queries"""
    coords = get_address_coordinates(address)
    return_text = ""
    if coords:
        return_text += f"Latitude: {coords.lat}, Longitude: {coords.lon}"
    else:
        return_text += "Address not found"
    bounding_box = get_bounding_box(coords.lat, coords.lon, distance)
    return bounding_box


def get_bounds_by_coords(lat: float, lon: float, distance: int) -> Optional[BoundingBox]:
    """Use a latitiude and longitude to create a box for overpass queries"""
    return_text = ""
    if validate_coordinates(lat, lon):
        bounding_box = get_bounding_box(lat, lon, distance)
        return bounding_box
    return None


def get_address_coordinates(address: str) -> Optional[Coordinates]:
    """Geocode and address into a latitude and longitude"""
    params = {"q": address, "format": "json", "limit": 1}
    headers = {"User-Agent": "MCP-Server/1.0 (jonny.mccullagh@gmail.com)"}
    response = requests.get(
        config.NOMINATIM_BASE_URL + "/search", params=params, headers=headers
    )
    if response.status_code == 200:
        data = response.json()
        if data:
            return Coordinates(lat=float(data[0]["lat"]), lon=float(data[0]["lon"]))
    return None


def get_address_from_coordinates(lat: float, lon: float) -> Optional[str]:
    """Find an address for the provided latitude and longitude"""
    params = {"lat": lat, "lon": lon, "extratags": 1, "format": "json"}
    headers = {
        "User-Agent": "Puca-Mcp-Server/1.0 (jonny.mccullagh@gmail.com)"
    }
    response = requests.get(
        config.NOMINATIM_BASE_URL + "/reverse", params=params, headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        logger.debug("Reverse address lookup returned: %s", data)
        if "display_name" in data:
            return data["display_name"]
    return None


def validate_coordinates(lat, lon):
    """Check that values are valid latitudes and longitudes"""
    try:
        # Convert to floats
        lat = float(lat)
        lon = float(lon)
        # Validate latitude and longitude ranges
        return bool(-90 <= lat <= 90 and -180 <= lon <= 180)
    except (ValueError, TypeError):
        # Invalid format (e.g., cannot convert to float)
        return False
