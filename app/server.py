import requests
import argparse
import asyncio
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
import math
import config
import overpy
from puca.utils import setup_logger, get_address_coordinates, get_address_from_coordinates, get_bounding_box, get_bounds_by_address, get_building_name, get_distance_between_points, validate_coordinates
from puca.emergency import defibrillators
from puca.amenity import get_amenity
from puca.thoroughfare import irish_street_names
from geopy.distance import geodesic
from geopy.point import Point
from mcp.server.fastmcp import FastMCP
import os

logger = setup_logger(config)

# Load environment variables
load_dotenv()
mcp = FastMCP("puca")

@mcp.tool()
async def get_defibrillators(address: str, distance: int = config.DISTANCE) -> str:
    """Get locations of defibrillators/AEDs within a radius around a given address

    Args:
        address: A valid address 
        distance: The number of metres radius around the address to check
    """
    return_text = ""
    coords = get_address_coordinates(address)
    if not coords or not validate_coordinates(coords.lat, coords.lon):
        return "Unable to get valid coordinates for the address requested. Please check the spelling of the address."
    bounding_box = get_bounds_by_address(address = address, distance = distance)
    defibs = defibrillators(bounding_box)
    return_text += f"\n{len(defibs.nodes)} defibrillators found within {distance} metre radius of {address}."
    for node in defibs.nodes:
        logger.debug(f"Distance between {coords.lat}, {coords.lon}, {node.lat}, {node.lon}")
        distance_metres = int(get_distance_between_points(coords.lat, coords.lon, node.lat, node.lon))
        node_address = get_address_from_coordinates(node.lat, node.lon)
        building_name = get_building_name(node.lat, node.lon)
        return_text += f"\n{distance_metres} metres away: {building_name} {node_address[:30]} Latitude: {node.lat}, Longitude: {node.lon}, Access: {node.tags.get('access', 'Not known')}, Inside: {node.tags.get('indoor', 'Not known')}, Find it: {node.tags.get('defibrillator:location', '')} URL: https://openstreetmap.org/node/{node.id} "
    return return_text


@mcp.tool()
async def get_distance_between_addresses(address1: str, address2: str) -> str:
    """Get the distance in metres between two addresses. The addresses are converted to
       coordinates and OSRM is queried to get a route between the points and the route distance.

    Args:
        address1: A valid address
        address1: A valid address
    """
    coords1 = get_address_coordinates(address1)
    coords2 = get_address_coordinates(address2)
    if not coords1 or not validate_coordinates(coords1.lat, coords1.lon):
        return "Unable to get valid coordinates for the address requested. Please check the values of {coords2.lat},{coords2.lon}"
    if not coords2 or not validate_coordinates(coords2.lat, coords2.lon):
        return "Unable to get valid coordinates for the address requested. Please check the values of {coords2.lat},{coords2.lon}"
    distance = get_distance_between_points(coords1.lat, coords1.lon, coords2.lat, coords2.lon)
    return f"\nThere are {distance} metres between {address1} and {address2}."


@mcp.tool()
async def get_distance_between_coords(lat1: float, lon1: float, lat2: float, lon2: float) -> str:
    """Get the distance in metres between two sets of coordinates.
       OSRM is queried to get a route between the points and the route distance.

    Args:
        lat1: A valid latitude between -90 and 90
        lon1: A valid longitude between -180 and 180
        lat2: A valid latitude between -90 and 90
        lon2: A valid longitude between -180 and 180
    """
    if not validate_coordinates(lat1, lon1) or not validate_coordinates(lat2, lon2):
        return "Unable to get valid coordinates for this request."
    distance = get_distance_between_points(lat1, lon1, lat2, lon2)
    return f"\nThere are {distance} metres between {lat1},{lon1} and {lat2},{lon2}."


@mcp.tool()
async def get_parking(address: str, distance: int = config.DISTANCE) -> str:
    """Get details about parking available within a radius around an address
       This will only show results of parking that has been added by volunteers to OpenStreetMap.

    Args:
        address: A valid address 
        distance: The number of metres radius around the address to check
    """
    return_text = ""
    bounding_box = get_bounds_by_address(address = address, distance = distance)
    carparks = get_amenity(type="parking", bounding_box = bounding_box)
    return_text += f"\nThere are {len(carparks.nodes)} parking amenities within {distance} metres of {address}."
    for node in carparks.nodes:
        node_address = get_address_from_coordinates(node.lat, node.lon)
        return_text += f"\nhttps://openstreetmap.org/node/{node.id}  {node_address} Latitude: {node.lat}, Longitude: {node.lon}, Access: {node.tags.get('access', 'Not known')}, Capacity: {node.tags.get('capacity', 'Not known')}, Cost: {node.tags.get('fee', '')}"
    return return_text

@mcp.tool()
async def get_toilets(address: str, distance: int = config.DISTANCE) -> str:
    """Get details about public toilets available within a radius around an address
       This will only show results of parking that has been added by volunteers to OpenStreetMap.

    Args:
        address: A valid address 
        distance: The number of metres radius around the address to check
    """
    type = "toilets"
    return_text = ""
    bounding_box = get_bounds_by_address(address = address, distance = distance)
    results_list = get_amenity(type=type, bounding_box = bounding_box)
    return_text += f"\nThere are {len(results_list.nodes)} {type} within {distance} metres of {address}."
    for node in results_list.nodes:
        node_address = get_address_from_coordinates(node.lat, node.lon)
        return_text += f"\n{node_address} Latitude: {node.lat}, Longitude: {node.lon}, Access: {node.tags.get('access', 'Not known')}, Cost: {node.tags.get('fee', '')} URL: https://openstreetmap.org/node/{node.id}"
    return return_text

@mcp.tool()
async def get_post_offices(address: str, distance: int = config.DISTANCE) -> str:
    """Get details about post offices available within a radius around an address
       This will only show results of parking that has been added by volunteers to OpenStreetMap.

    Args:
        address: A valid address 
        distance: The number of metres radius around the address to check
    """
    type = "post_office"
    return_text = ""
    bounding_box = get_bounds_by_address(address = address, distance = distance)
    results_list = get_amenity(type=type, bounding_box = bounding_box)
    return_text += f"\nThere are {len(results_list.nodes)} {type} within {distance} metres of {address}."
    for node in results_list.nodes:
        node_address = get_address_from_coordinates(node.lat, node.lon)
        return_text += f"\n{node_address} Latitude: {node.lat}, Longitude: {node.lon}, Access: {node.tags.get('access', 'Not known')}, Cost: {node.tags.get('fee', '')} URL: https://openstreetmap.org/node/{node.id}"
    return return_text

@mcp.tool()
async def get_cafes(address: str, distance: int = config.DISTANCE) -> str:
    """Get locations of Coffee Shops/Cafes within a radius around an address

    Args:
        address: A valid address 
        distance: The number of metres radius around the address to check
    """
    type = "cafe"
    return_text = ""
    bounding_box = get_bounds_by_address(address = address, distance = distance)
    results_list = get_amenity(type=type, bounding_box = bounding_box)
    return_text += f"\nThere are {len(results_list.nodes)} {type} within {distance} metres of {address}."
    for node in results_list.nodes:
        node_address = get_address_from_coordinates(node.lat, node.lon)
        return_text += f"\n{node_address} Latitude: {node.lat}, Longitude: {node.lon}, Access: {node.tags.get('access', 'Not known')}, Cost: {node.tags.get('fee', '')} URL: https://openstreetmap.org/node/{node.id}"
    return return_text

@mcp.tool()
async def get_fast_food_places(address: str, distance: int = config.DISTANCE) -> str:
    """Get locations of Fast Food establishments within a radius around an address

    Args:
        address: A valid address 
        distance: The number of metres radius around the address to check
    """
    type = "fast_food"
    return_text = ""
    bounding_box = get_bounds_by_address(address = address, distance = distance)
    results_list = get_amenity(type=type, bounding_box = bounding_box)
    return_text += f"\nThere are {len(results_list.nodes)} {type} places within {distance} metres of {address}."
    for node in results_list.nodes:
        node_address = get_address_from_coordinates(node.lat, node.lon)
        return_text += f"\n{node_address} Latitude: {node.lat}, Longitude: {node.lon}, Access: {node.tags.get('access', 'Not known')}, Cost: {node.tags.get('fee', '')} URL: https://openstreetmap.org/node/{node.id}"
    return return_text

@mcp.tool()
async def get_irish_street_names(address: str, distance: int = config.DISTANCE) -> str:
    """Get the names of streets that have a Irish language translation within a radius around an address

    Args:
        address: A valid address 
        distance: The number of metres radius around the address to check
    """
    return_text = ""
    bounding_box = get_bounds_by_address(address = address, distance = distance)
    results_list = irish_street_names(bounding_box = bounding_box)
    return_text += f"\nThere are {len(results_list.ways)} thoroughfares with an Irish translation within {distance} metres of {address}."
    observed_ways = []
    for way in results_list.ways:
        if way.tags['name'] not in observed_ways:
            observed_ways.append(way.tags['name'])
            return_text += f"\n {way.tags['name:ga']}, {way.tags['name']}, URL: https://openstreetmap.org/node/{way.id}"
    return return_text


if __name__ == "__main__":
    # Initialize and run the server
    parser = argparse.ArgumentParser(description="Run the server or perform local operations.")
    parser.add_argument('--local', action='store_true', help='Run in local mode.')
    parser.add_argument('--address', type=str, help='Address for local operations.')
    parser.add_argument('--distance', type=int, help='Search radius in metres')
    # Parse the arguments
    args = parser.parse_args()

    if args.local:
        # Check if address is provided
        if not args.address:
            print("Error: --address must be provided when using --local.")
        else:
            print(asyncio.run(get_irish_street_names(address = args.address, distance = args.distance)))
            # print(asyncio.run(get_post_offices(address = args.address, distance = args.distance)))
    else:
        # Default to running the server
        mcp.run(transport='stdio')
