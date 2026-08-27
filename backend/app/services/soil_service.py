from typing import Dict, Any
from ..integrations.soil_provider import OpenMeteoSoilProvider, SampleSoilProvider
import logging

logger = logging.getLogger(__name__)

class SoilService:
    def __init__(self):
        self.live_provider = OpenMeteoSoilProvider()
        self.sample_provider = SampleSoilProvider()
        self.cache: Dict[str, Dict[str, Any]] = {}

    def get_soil_data(self, lat: float, lon: float) -> Dict[str, Any]:
        cache_key = f"{round(lat, 2)}_{round(lon, 2)}"
        if cache_key in self.cache:
            cached = self.cache[cache_key].copy()
            cached["source"] = "CACHED"
            return cached

        data = self.live_provider.get_soil_profile(lat, lon)
        if not data or not data.get("soil_type"):
            data = self.sample_provider.get_soil_profile(lat, lon)

        self.cache[cache_key] = data
        return data

soil_service = SoilService()
