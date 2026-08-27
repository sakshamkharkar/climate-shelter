from pydantic import BaseModel, Field
from typing import Optional, List

class LocationQuery(BaseModel):
    query: str = Field(..., description="City or region name to search")

class LocationSearchResult(BaseModel):
    name: str
    latitude: float
    longitude: float
    country: Optional[str] = None
    elevation: Optional[float] = None
    timezone: Optional[str] = None

class LocationSearchResponse(BaseModel):
    results: List[LocationSearchResult]
    source: str = "LIVE"  # LIVE, CACHED, SAMPLE
