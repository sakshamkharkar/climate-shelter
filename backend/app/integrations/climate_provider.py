from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import requests
import logging

logger = logging.getLogger(__name__)

class ClimateProvider(ABC):
    @abstractmethod
    def geocode_location(self, query: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        pass

class OpenMeteoClimateProvider(ClimateProvider):
    def geocode_location(self, query: str) -> List[Dict[str, Any]]:
        try:
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=5&language=en&format=json"
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                data = res.json()
                results = data.get("results", [])
                out = []
                for item in results:
                    out.append({
                        "name": item.get("name"),
                        "latitude": item.get("latitude"),
                        "longitude": item.get("longitude"),
                        "country": item.get("country"),
                        "elevation": item.get("elevation", 0.0),
                        "timezone": item.get("timezone", "UTC")
                    })
                return out
        except Exception as e:
            logger.warning(f"Open-Meteo Geocoding failed: {e}")
        return []

    def get_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        try:
            url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={lat}&longitude={lon}&"
                f"current=temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,wind_direction_10m,shortwave_radiation&"
                f"hourly=temperature_2m&"
                f"daily=temperature_2m_max,temperature_2m_min,rain_sum&"
                f"forecast_days=1"
            )
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                data = res.json()
                curr = data.get("current", {})
                daily = data.get("daily", {})
                hourly = data.get("hourly", {})
                
                temp = curr.get("temperature_2m", 15.0)
                temp_max = daily.get("temperature_2m_max", [temp + 5.0])[0]
                temp_min = daily.get("temperature_2m_min", [temp - 5.0])[0]
                
                return {
                    "source": "LIVE",
                    "average_temperature": temp,
                    "maximum_temperature": temp_max,
                    "minimum_temperature": temp_min,
                    "humidity": curr.get("relative_humidity_2m", 50.0),
                    "solar_radiation": curr.get("shortwave_radiation", 600.0) or 550.0,
                    "wind_speed": curr.get("wind_speed_10m", 5.0),
                    "wind_direction": curr.get("wind_direction_10m", 180.0),
                    "pressure": curr.get("surface_pressure", 1013.25),
                    "rainfall": daily.get("rain_sum", [0.0])[0] or 0.0,
                    "elevation": data.get("elevation", 0.0),
                    "hourly_temperatures": hourly.get("temperature_2m", [])
                }
        except Exception as e:
            logger.warning(f"Open-Meteo Weather API failed: {e}")
        return {}

class SampleClimateProvider(ClimateProvider):
    def geocode_location(self, query: str) -> List[Dict[str, Any]]:
        samples = [
            {"name": "Leh, Ladakh", "latitude": 34.1526, "longitude": 77.5771, "country": "India", "elevation": 3500.0, "timezone": "Asia/Kolkata"},
            {"name": "Cairo, Egypt", "latitude": 30.0444, "longitude": 31.2357, "country": "Egypt", "elevation": 23.0, "timezone": "Africa/Cairo"},
            {"name": "Reykjavik, Iceland", "latitude": 64.1466, "longitude": -21.9426, "country": "Iceland", "elevation": 15.0, "timezone": "Atlantic/Reykjavik"},
            {"name": "Phoenix, Arizona", "latitude": 33.4484, "longitude": -112.0740, "country": "United States", "elevation": 331.0, "timezone": "America/Phoenix"},
            {"name": "La Paz, Bolivia", "latitude": -16.5000, "longitude": -68.1500, "country": "Bolivia", "elevation": 3640.0, "timezone": "America/La_Paz"},
        ]
        q_lower = query.lower()
        matched = [s for s in samples if q_lower in s["name"].lower()]
        return matched if matched else [samples[0]]

    def get_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        # Generate sample weather profiles based on latitude
        if lat > 50.0 or lat < -50.0 or (30 < lat < 40 and lon > 70):  # Cold high altitude e.g. Leh / Iceland
            return {
                "source": "SAMPLE",
                "average_temperature": -12.0,
                "maximum_temperature": -5.0,
                "minimum_temperature": -21.0,
                "humidity": 25.0,
                "solar_radiation": 850.0,
                "wind_speed": 12.0,
                "wind_direction": 190.0,
                "pressure": 610.0,
                "rainfall": 1.2,
                "elevation": 3500.0,
                "hourly_temperatures": [-18, -20, -21, -17, -12, -10, -14, -19, -18]
            }
        elif 0 <= lat <= 35:  # Hot arid / desert
            return {
                "source": "SAMPLE",
                "average_temperature": 36.5,
                "maximum_temperature": 44.0,
                "minimum_temperature": 28.0,
                "humidity": 20.0,
                "solar_radiation": 980.0,
                "wind_speed": 4.5,
                "wind_direction": 140.0,
                "pressure": 1008.0,
                "rainfall": 0.0,
                "elevation": 150.0,
                "hourly_temperatures": [28, 27, 26, 30, 37, 43, 44, 40, 33]
            }
        else:  # Temperate
            return {
                "source": "SAMPLE",
                "average_temperature": 18.0,
                "maximum_temperature": 24.0,
                "minimum_temperature": 12.0,
                "humidity": 65.0,
                "solar_radiation": 650.0,
                "wind_speed": 6.0,
                "wind_direction": 220.0,
                "pressure": 1015.0,
                "rainfall": 5.4,
                "elevation": 200.0,
                "hourly_temperatures": [12, 11, 10, 14, 19, 23, 24, 20, 15]
            }
