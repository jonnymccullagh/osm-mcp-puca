from pydantic import BaseModel


class Coordinates(BaseModel):
    lat: float
    lon: float


class BoundingBox(BaseModel):
    top_left_lat: float
    top_left_lon: float
    bottom_right_lat: float
    bottom_right_lon: float

# Create a logger configuration model
class LoggerConfig(BaseModel):
    name: str = __name__
    level: str = "INFO"
    format: str = "%(asctime)s - %(levelname)s - %(message)s"
    output: str = "stdout"  # "stdout" or a file path