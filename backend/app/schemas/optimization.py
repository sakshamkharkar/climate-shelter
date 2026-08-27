from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from .environment import EnvironmentalProfile
from .design import DesignCandidate

class OptimizationRequest(BaseModel):
    environment: EnvironmentalProfile
    target_temperature: float = 21.0  # Ideal interior comfort temp °C
    priority: str = "thermal_comfort"  # thermal_comfort, cost, sustainable, autonomy
    weight_thermal: float = 0.6
    weight_cost: float = 0.2
    weight_weight: float = 0.2
    max_candidates_to_search: int = 250

class OptimizationResponse(BaseModel):
    id: str
    best_design: DesignCandidate
    alternatives: List[DesignCandidate]
    total_evaluated: int
    execution_time_ms: float
    optimization_objective: str
    timestamp: str

class SiteOptimizationResult(BaseModel):
    site_name: str
    latitude: float
    longitude: float
    best_design: DesignCandidate
    predicted_interior_temp: float
    outdoor_avg_temp: float

class MultiSiteOptimizationRequest(BaseModel):
    sites: List[Dict[str, Any]]  # [{name, latitude, longitude}]
    priority: str = "thermal_comfort"

class MultiSiteOptimizationResponse(BaseModel):
    results: List[SiteOptimizationResult]
    timestamp: str

