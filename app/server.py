"""
Runs the MCP server and provides tools to the calling LLM
"""
import argparse
import asyncio
import math
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import config
from puca.utils import (
    setup_logger,
    get_address_coordinates,
    get_address_from_coordinates,
    get_bounds_by_address,
    get_bounds_by_coords,
    get_building_name,
    get_distance_between_points,
    validate_coordinates,
)
from puca.emergency import defibrillators
from puca.building import school, kindergarten, retail, vacant
from puca.amenity import get_amenity
from puca.thoroughfare import irish_street_names


logger = setup_logger(config)

# Load environment variables
load_dotenv()
mcp = FastMCP("puca")


@mcp.tool()
async def get_coordinates_for_address(address: str) -> str:
    """Get the coordinates of a given address

    Args:
        address: A valid address
    """
    coords = get_address_coordinates(address)
    if not coords or not validate_coordinates(coords.lat, coords.lon):
        return "Unable to get valid coordinates for the address requested. Please check the spelling of the address."
    return f"Latitude: {coords.lat}, Longitude: {coords.lon}"


@mcp.tool()
async def get_address_by_coordinates(lat: float, lon: float) -> str:
    """Get the coordinates of a given address

    Args:
        address: A valid address
    """
    address = await get_address_from_coordinates(lat, lon)
    if not address:
        return "Unable to get valid coordinates for the address requested. Please check the spelling of the address."
    return f"Address: {address}"


@mcp.tool()
async def get_defibrillators(address: str, distance: int = config.DISTANCE) -> str:
    """Get locations of defibrillators/AEDs within a radius around a given address

    Args:
        address: A valid address
        distance: The number of metres radius around the address to check
    """
    return_text = ""
    coords = await get_address_coordinates(address)
    if not coords or not validate_coordinates(coords.lat, coords.lon):
        return "Unable to get valid coordinates for the address requested. Please check the spelling of the address."
    bounding_box = get_bounds_by_address(address=address, distance=distance)
    defibs = defibrillators(bounding_box)
    return_text += f"\n{len(defibs.nodes)} defibrillators found within {distance} metre radius of {address}."
    for node in defibs.nodes:
        logger.debug(
            "Distance between %s, %s, %s, %s", coords.lat, coords.lon, node.lat, node.lon
        )
        distance_metres = int(
            get_distance_between_points(coords.lat, coords.lon, node.lat, node.lon)
        )
        node_address = await get_address_from_coordinates(node.lat, node.lon)
        building_name = await get_building_name(node.lat, node.lon)
        return_text += (
            f"\n{distance_metres} metres away: {building_name} {node_address[:30]} "
            f"Latitude: {node.lat}, Longitude: {node.lon}, Access: {node.tags.get('access', 'Not known')}, "
            f"Inside: {node.tags.get('indoor', 'Not known')}, "
            f"Find it: {node.tags.get('defibrillator:location', '')} "
            f"URL: https://openstreetmap.org/node/{node.id}"
        )
    return return_text


@mcp.tool()
async def get_distance_between_addresses(address1: str, address2: str) -> str:
    """Get the distance in metres between two addresses. The addresses are converted to
       coordinates and OSRM is queried to get a route between the points and the route distance.

    Args:
        address1: A valid address
        address1: A valid address
    """
    coords1 = await get_address_coordinates(address1)
    coords2 = await get_address_coordinates(address2)
    if not coords1 or not validate_coordinates(coords1.lat, coords1.lon):
        return "Unable to get valid coordinates for address. Check the values of {coords2.lat},{coords2.lon}"
    if not coords2 or not validate_coordinates(coords2.lat, coords2.lon):
        return "Unable to get valid coordinates for address. Check the values of {coords2.lat},{coords2.lon}"
    distance = get_distance_between_points(
        coords1.lat, coords1.lon, coords2.lat, coords2.lon
    )
    return f"\nThere are {distance} metres between {address1} and {address2}."


@mcp.tool()
async def get_distance_between_coords(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> str:
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
    bounding_box = get_bounds_by_address(address=address, distance=distance)
    parking = get_amenity(amenity="parking", bounding_box=bounding_box)
    return_text += f"\nThere are {len(parking.ways)} parking amenities within {distance} metres of {address}."
    for way in parking.ways:
        way_text = ""
        way_text += f"Name: {way.tags.get('name')}, " if way.tags.get("name") else ""
        way_text += (
            f"Type: {way.tags.get('parking')}, " if way.tags.get("parking") else ""
        )
        way_text += (
            f"Access: {way.tags.get('access')}, " if way.tags.get("access") else ""
        )
        way_text += (
            f"Operator: {way.tags.get('operator')}, "
            if way.tags.get("operator")
            else ""
        )
        way_text += (
            f"Capacity: {way.tags.get('capacity')}, "
            if way.tags.get("capacity")
            else ""
        )
        way_text += f"Cost: {way.tags.get('fee')}, " if way.tags.get("fee") else ""
        way_text += (
            f"Surface Type: {way.tags.get('surface')}, "
            if way.tags.get("surface")
            else ""
        )
        return_text += f"\n {way_text} URL: https://openstreetmap.org/way/{way.id}"
    return return_text


@mcp.tool()
async def get_toilets(address: str, distance: int = config.DISTANCE) -> str:
    """Get details about public toilets available within a radius around an address
       This will only show results of parking that has been added by volunteers to OpenStreetMap.

    Args:
        address: A valid address
        distance: The number of metres radius around the address to check
    """
    amenity = "toilets"
    return_text = ""
    bounding_box = get_bounds_by_address(address=address, distance=distance)
    results_list = get_amenity(amenity=amenity, bounding_box=bounding_box)
    return_text += f"\nThere are {len(results_list.nodes)} {amenity} within {distance} metres of {address}."
    for node in results_list.nodes:
        for tag in node.tags:
            return_text += f"{tag}: {node.tags[tag]},"
        return_text += f" URL: https://openstreetmap.org/node/{node.id}\n"
    for way in results_list.ways:
        for tag in way.tags:
            return_text += f"{tag}: {way.tags[tag]},"
        return_text += f" URL: https://openstreetmap.org/way/{way.id}\n"
    return return_text


@mcp.tool()
async def get_post_offices(address: str, distance: int = config.DISTANCE) -> str:
    """Get details about post offices available within a radius around an address
       This will only show results of parking that has been added by volunteers to OpenStreetMap.

    Args:
        address: A valid address
        distance: The number of metres radius around the address to check
    """
    amenity = "post_office"
    return_text = ""
    bounding_box = get_bounds_by_address(address=address, distance=distance)
    results_list = get_amenity(amenity=amenity, bounding_box=bounding_box)
    return_text += f"\nThere are {len(results_list.nodes)} {amenity} places within {distance} metres of {address}."
    for node in results_list.nodes:
        for tag in node.tags:
            return_text += f"{tag}: {node.tags[tag]},"
        return_text += f" URL: https://openstreetmap.org/node/{node.id}\n"
    for way in results_list.ways:
        for tag in way.tags:
            return_text += f"{tag}: {way.tags[tag]},"
        return_text += f" URL: https://openstreetmap.org/way/{way.id}\n"
    return return_text
    return return_text


@mcp.tool()
async def get_cafes(address: str, distance: int = config.DISTANCE) -> str:
    """Get locations of Coffee Shops/Cafes within a radius around an address

    Args:
        address: A valid address
        distance: The number of metres radius around the address to check
    """
    amenity = "cafe"
    return_text = ""
    bounding_box = get_bounds_by_address(address=address, distance=distance)
    results_list = get_amenity(amenity=amenity, bounding_box=bounding_box)
    return_text += f"\nThere are {len(results_list.nodes)} {amenity} places within {distance} metres of {address}."
    for node in results_list.nodes:
        for tag in node.tags:
            return_text += f"{tag}: {node.tags[tag]},"
        return_text += f" URL: https://openstreetmap.org/node/{node.id}\n"
    for way in results_list.ways:
        for tag in way.tags:
            return_text += f"{tag}: {way.tags[tag]},"
        return_text += f" URL: https://openstreetmap.org/way/{way.id}\n"
    return return_text


@mcp.tool()
async def get_fast_food_places(address: str, distance: int = config.DISTANCE) -> str:
    """Get locations of Fast Food establishments within a radius around an address

    Args:
        address: A valid address
        distance: The number of metres radius around the address to check
    """
    amenity = "fast_food"
    return_text = ""
    bounding_box = get_bounds_by_address(address=address, distance=distance)
    results_list = get_amenity(amenity=amenity, bounding_box=bounding_box)
    return_text += f"\nThere are {len(results_list.nodes)} {amenity} places within {distance} metres of {address}."
    for node in results_list.nodes:
        for tag in node.tags:
            return_text += f"{tag}: {node.tags[tag]},"
        return_text += f" URL: https://openstreetmap.org/node/{node.id}\n"
    for way in results_list.ways:
        for tag in way.tags:
            return_text += f"{tag}: {way.tags[tag]},"
        return_text += f" URL: https://openstreetmap.org/way/{way.id}\n"
    return return_text


@mcp.tool()
async def get_irish_street_names(address: str, distance: int = config.DISTANCE) -> str:
    """Get the names of streets that have a Irish language translation within a radius around an address

    Args:
        address: A valid address
        distance: The number of metres radius around the address to check
    """
    return_text = ""
    bounding_box = get_bounds_by_address(address=address, distance=distance)
    results_list = irish_street_names(bounding_box=bounding_box)
    return_text += (
        f"\nFound {len(results_list.ways)} thoroughfares with an "
        f"Irish name within {distance} metres of {address}."
    )
    observed_ways = []
    for way in results_list.ways:
        if way.tags["name"] not in observed_ways:
            observed_ways.append(way.tags["name"])
            return_text += f"\n {way.tags['name:ga']}, {way.tags['name']}, URL: https://openstreetmap.org/node/{way.id}"
    return return_text


@mcp.tool()
async def get_vacant_buildings(address: str, distance: int = config.DISTANCE) -> str:
    """List buildings marked as vacant/disused within a radius around an address

    Args:
        address: A valid address
        distance: The number of metres radius around the address to check
    """
    return_text = ""
    bounding_box = get_bounds_by_address(address=address, distance=distance)
    results_list = vacant(bounding_box=bounding_box)
    area_sq_km = (
        math.pi * (distance * distance) / 1_000_000
    )
    # Calculate ratio of vacant/disused buildings per square kilometer
    if area_sq_km > 0:  # Avoid division by zero
        ratio = len(results_list.ways) / area_sq_km
    else:
        ratio = 0
    return_text += (
        f"\nFound {len(results_list.ways)} buildings marked "
         f"as vacant within {distance} metres of {address}.\n"
    )
    return_text += f"This corresponds to a ratio of {ratio:.2f} vacant buildings per square kilometer.\n"
    for way in results_list.ways:
        for tag in way.tags:
            return_text += f"{tag}: {way.tags[tag]},"
        return_text += f" URL: https://openstreetmap.org/way/{way.id}\n"
    for node in results_list.nodes:
        for tag in node.tags:
            return_text += f"{tag}: {node.tags[tag]},"
        return_text += f" URL: https://openstreetmap.org/node/{node.id}\n"
    return return_text


@mcp.tool()
def query_overpass(query: str, lat: float, lon: float, distance: int = config.DISTANCE) -> str:
    """
    Queries the Overpass API with a custom query and returns the results.
    Args:
        query: The Overpass API query to execute. A template is used to set the output and bounding search area so only the raw search terms are needed e.g. nwr["building"="school"]
        lat: Latitude of the center point for the bounding box.
        lon: Longitude of the center point for the bounding box.
        distance: The radius in meters around the center point.
    """
    bounding_box = get_bounds_by_coords(lat, lon, distance)
    result = query_overpass(query, bounding_box) 
    return_text = ""
    for way in result.ways:
        for tag in way.tags:
            return_text += f"{tag}: {way.tags[tag]},"
        return_text += f" URL: https://openstreetmap.org/way/{way.id}\n"
    for node in result.nodes:
        for tag in node.tags:
            return_text += f"{tag}: {node.tags[tag]},"
        return_text += f" URL: https://openstreetmap.org/node/{node.id}\n"
    for relation in result.relations:
        for tag in relation.tags:
            return_text += f"{tag}: {relation.tags[tag]},"
        return_text += f" URL: https://openstreetmap.org/relation/{relation.id}\n"
    return return_text


if __name__ == "__main__":
    # Initialize and run the server
    parser = argparse.ArgumentParser(
        description="Run the server or perform local operations."
    )
    parser.add_argument("--local", action="store_true", help="Run in local mode.")
    parser.add_argument("--address", type=str, help="Address for local operations.")
    parser.add_argument("--distance", type=int, help="Search radius in metres")
    # Parse the arguments
    args = parser.parse_args()

    if args.local:
        # Check if address is provided
        if not args.address:
            print("Error: --address must be provided when using --local.")
        else:
            print(
                asyncio.run(
                    get_vacant_buildings(address=args.address, distance=args.distance)
                )
            )
            # print(asyncio.run(get_parking(address = args.address, distance = args.distance)))
            # print(asyncio.run(get_irish_street_names(address = args.address, distance = args.distance)))
            # print(asyncio.run(get_post_offices(address = args.address, distance = args.distance)))
    else:
        # Default to running the server
        mcp.run(transport="sse")
