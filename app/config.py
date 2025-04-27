import os

# Application Base Configuration
NOMINATIM_BASE_URL = os.getenv("NOMINATIM_BASE_URL", "https://nominatim.openstreetmap.org")
OSRM_BASE_URL = os.getenv("OSRM_BASE_URL", "https://router.project-osrm.org/route/v1/driving")
OVERPASS_BASE_URL = os.getenv("OVERPASS_BASE_URL", "https://overpass-api.de/api/interpreter")
DISTANCE = float(os.getenv("DISTANCE", 100.0))  # Default distance in meters
level = os.getenv("LOG_LEVEL", "DEBUG")
output = os.getenv("LOG_TO", "stdout")
name = "puca"
format = "%(asctime)s - %(levelname)s - %(message)s"