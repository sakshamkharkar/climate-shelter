from typing import Dict, Any, List
from ..integrations.climate_provider import OpenMeteoClimateProvider, SampleClimateProvider, ClimateProvider
from ..config import settings
import logging

logger = logging.getLogger(__name__)

class ClimateService:
    def __init__(self):
        self.live_provider = OpenMeteoClimateProvider()
        self.sample_provider = SampleClimateProvider()
        self.cache: Dict[str, Dict[str, Any]] = {}

    def search_location(self, query: str) -> List[Dict[str, Any]]:
        results = self.live_provider.geocode_location(query)
        if not results:
            results = self.sample_provider.geocode_location(query)
        return results

    def get_climate_data(self, lat: float, lon: float) -> Dict[str, Any]:
        cache_key = f"{round(lat, 2)}_{round(lon, 2)}"
        if cache_key in self.cache:
            logger.info(f"Returning cached climate data for {cache_key}")
            cached = self.cache[cache_key].copy()
            cached["source"] = "CACHED"
            return cached

        # Try live first
        data = self.live_provider.get_weather(lat, lon)
        if not data or not data.get("average_temperature"):
            data = self.sample_provider.get_weather(lat, lon)

        self.cache[cache_key] = data
        return data

climate_service = ClimateService()
