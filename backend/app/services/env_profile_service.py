from typing import Dict, Any, Optional
from datetime import datetime
from ..schemas.environment import EnvironmentalProfile, SoilProperties
from .climate_service import climate_service
from .soil_service import soil_service

class EnvProfileService:
    def create_profile(
        self,
        lat: float,
        lon: float,
        location_name: Optional[str] = None
    ) -> EnvironmentalProfile:
        climate = climate_service.get_climate_data(lat, lon)
        soil = soil_service.get_soil_data(lat, lon)

        if not location_name:
            location_name = f"Loc ({round(lat, 2)}, {round(lon, 2)})"

        soil_props = SoilProperties(
            soil_type=soil.get("soil_type", "Sandy Clay Loam"),
            sand_percentage=soil.get("sand_percentage", 45.0),
            clay_percentage=soil.get("clay_percentage", 30.0),
            silt_percentage=soil.get("silt_percentage", 25.0),
            moisture_content=soil.get("moisture_content", 0.18),
            soil_temperature_10cm=soil.get("soil_temperature_10cm", 14.5),
            thermal_conductivity=soil.get("thermal_conductivity", 1.25)
        )

        return EnvironmentalProfile(
            latitude=lat,
            longitude=lon,
            location_name=location_name,
            elevation=climate.get("elevation", 0.0),
            average_temperature=climate.get("average_temperature", 15.0),
            minimum_temperature=climate.get("minimum_temperature", -5.0),
            maximum_temperature=climate.get("maximum_temperature", 35.0),
            humidity=climate.get("humidity", 45.0),
            solar_radiation=climate.get("solar_radiation", 750.0),
            wind_speed=climate.get("wind_speed", 8.5),
            wind_direction=climate.get("wind_direction", 180.0),
            rainfall=climate.get("rainfall", 0.0),
            pressure=climate.get("pressure", 1013.25),
            soil_properties=soil_props,
            data_source=climate.get("source", "LIVE"),
            timestamp=datetime.utcnow().isoformat() + "Z",
            hourly_temperatures=climate.get("hourly_temperatures", [])
        )

    def create_multi_profiles(self, sites: list) -> list:
        profiles = []
        for s in sites:
            name = s.get("name") or f"Site ({s.get('latitude')}, {s.get('longitude')})"
            prof = self.create_profile(s.get("latitude"), s.get("longitude"), name)
            profiles.append(prof)
        return profiles


env_profile_service = EnvProfileService()
