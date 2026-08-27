from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class DesignParameters(BaseModel):
    material_id: str = "stabilized_earth_block"
    wall_thickness: float = Field(0.30, ge=0.05, le=1.0, description="Wall thickness in meters")
    roof_thickness: float = Field(0.20, ge=0.05, le=0.8, description="Roof thickness in meters")
    length: float = Field(6.0, ge=2.0, le=20.0, description="Building length in meters")
    width: float = Field(4.0, ge=2.0, le=20.0, description="Building width in meters")
    height: float = Field(3.0, ge=2.0, le=6.0, description="Building height in meters")
    orientation: float = Field(180.0, ge=0.0, le=360.0, description="Azimuth angle in degrees (180=South)")
    insulation_thickness: float = Field(0.08, ge=0.0, le=0.30, description="Insulation thickness in meters")
    window_to_wall_ratio: float = Field(0.15, ge=0.0, le=0.60, description="Window-to-wall area ratio")

class ConstraintValidation(BaseModel):
    valid: bool
    violations: List[str] = Field(default_factory=list)

class DesignCandidate(BaseModel):
    id: str
    rank: int = 1
    parameters: DesignParameters
    material_name: str
    predicted_interior_temp: float
    objective_score: float
    constraint_status: ConstraintValidation
    thermal_comfort_score: float
    cost_index: float
