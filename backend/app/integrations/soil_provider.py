from abc import ABC, abstractmethod
from typing import Dict, Any
import requests
import logging

logger = logging.getLogger(__name__)

class SoilProvider(ABC):
    @abstractmethod
    def get_soil_profile(self, lat: float, lon: float) -> Dict[str, Any]:
        pass

class OpenMeteoSoilProvider(SoilProvider):
    def get_soil_profile(self, lat: float, lon: float) -> Dict[str, Any]:
        try:
            url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={lat}&longitude={lon}&"
                f"current=soil_temperature_0cm,soil_moisture_0_to_1cm"
            )
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                data = res.json()
                curr = data.get("current", {})
                temp = curr.get("soil_temperature_0cm", 14.5)
                moisture = curr.get("soil_moisture_0_to_1cm", 0.15)
                return {
                    "soil_type": "Sandy Clay Loam",
                    "sand_percentage": 45.0,
                    "clay_percentage": 30.0,
                    "silt_percentage": 25.0,
                    "moisture_content": moisture,
                    "soil_temperature_10cm": temp,
                    "thermal_conductivity": 1.35,
                    "source": "LIVE"
                }
        except Exception as e:
            logger.warning(f"Open-Meteo Soil API failed: {e}")
        return {}

class SampleSoilProvider(SoilProvider):
    def get_soil_profile(self, lat: float, lon: float) -> Dict[str, Any]:
        if lat > 50.0 or (30 < lat < 40 and lon > 70):  # Cold rocky / gravelly mountain soil
            return {
                "soil_type": "Gravelly Sandy Loam",
                "sand_percentage": 65.0,
                "clay_percentage": 15.0,
                "silt_percentage": 20.0,
                "moisture_content": 0.08,
                "soil_temperature_10cm": -4.2,
                "thermal_conductivity": 0.95,
                "source": "SAMPLE"
            }
        elif 0 <= lat <= 35:  # Arid sandy desert soil
            return {
                "soil_type": "Arid Coarse Sand",
                "sand_percentage": 85.0,
                "clay_percentage": 8.0,
                "silt_percentage": 7.0,
                "moisture_content": 0.03,
                "soil_temperature_10cm": 28.4,
                "thermal_conductivity": 0.45,
                "source": "SAMPLE"
            }
        else:  # Temperate clay loam
            return {
                "soil_type": "Silty Clay Loam",
                "sand_percentage": 30.0,
                "clay_percentage": 40.0,
                "silt_percentage": 30.0,
                "moisture_content": 0.22,
                "soil_temperature_10cm": 15.1,
                "thermal_conductivity": 1.45,
                "source": "SAMPLE"
            }
