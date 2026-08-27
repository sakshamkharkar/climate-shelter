from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from .design import DesignParameters
from .environment import EnvironmentalProfile

class SimulationRunRequest(BaseModel):
    design: DesignParameters
    environment: EnvironmentalProfile

class SimulationRunResponse(BaseModel):
    simulation_id: str
    ansys_mode: str  # REAL, MOCK
    status: str  # COMPLETED, FAILED, RUNNING
    interior_temperature: float
    max_surface_temp: float
    min_surface_temp: float
    total_heat_flux: float
    execution_time_seconds: float
    apdl_script_preview: str
    data_source_label: str  # "MOCK: External ANSYS execution not connected" or "LIVE: ANSYS APDL Solver"
    timestamp: str

class ValidationRunResponse(BaseModel):
    validation_id: str
    design_id: str
    ml_prediction_temp: float
    ansys_simulation_temp: float
    absolute_error: float  # °C
    relative_error_percentage: float  # %
    model_version: str
    ansys_mode: str
    passed_validation: bool
    timestamp: str
