from pydantic import BaseModel
from typing import Optional

class Material(BaseModel):
    id: str
    name: str
    thermal_conductivity: float  # W/(m·K)
    density: float  # kg/m³
    specific_heat: float  # J/(kg·K)
    cost_estimate: float  # USD/m³ or relative index
    availability: str = "High"  # High, Medium, Low, Regional
    source: str = "Engineering Database"  # VERIFIED, SAMPLE
    description: Optional[str] = None

class MaterialComparisonItem(BaseModel):
    material_id: str
    material_name: str
    thermal_conductivity: float
    density: float
    specific_heat: float
    cost_estimate: float
    availability: str
    predicted_interior_temp: float
    thermal_comfort_score: float
    volumetric_heat_capacity: float  # kJ/(m³·K)
    suitability_rank: int

class MaterialComparisonResponse(BaseModel):
    location_name: str
    outdoor_avg_temp: float
    materials: List[MaterialComparisonItem]

