from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class SoilProperties(BaseModel):
    soil_type: str = "Sandy Clay Loam"
    sand_percentage: float = 45.0
    clay_percentage: float = 30.0
    silt_percentage: float = 25.0
    moisture_content: float = 0.18
    soil_temperature_10cm: float = 14.5
    thermal_conductivity: float = 1.25  # W/m.K

class EnvironmentalProfile(BaseModel):
    latitude: float
    longitude: float
    location_name: str = "Unknown Location"
    elevation: float = 0.0
    average_temperature: float = 15.0  # °C
    minimum_temperature: float = -5.0  # °C
    maximum_temperature: float = 35.0  # °C
    humidity: float = 45.0  # %
    solar_radiation: float = 750.0  # W/m²
    wind_speed: float = 8.5  # m/s
    wind_direction: float = 180.0  # deg
    rainfall: float = 12.0  # mm
    pressure: float = 850.0  # hPa
    soil_properties: SoilProperties = Field(default_factory=SoilProperties)
    data_source: str = "LIVE"  # LIVE, CACHED, SAMPLE, UNAVAILABLE
    timestamp: str = ""
    hourly_temperatures: List[float] = Field(default_factory=list)

class EnvProfileRequest(BaseModel):
    latitude: float = 34.1526
    longitude: float = 77.5771
    location_name: Optional[str] = "Leh, Ladakh"

class SiteCoordinateInput(BaseModel):
    name: str
    latitude: float
    longitude: float

class MultiSiteProfileRequest(BaseModel):
    sites: List[SiteCoordinateInput]

class MultiSiteProfileResponse(BaseModel):
    profiles: List[EnvironmentalProfile]

