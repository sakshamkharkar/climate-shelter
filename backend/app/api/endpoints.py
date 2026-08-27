from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Dict, Any

from ..schemas.location import LocationQuery, LocationSearchResponse, LocationSearchResult
from ..schemas.environment import EnvProfileRequest, EnvironmentalProfile
from ..schemas.material import Material
from ..schemas.design import DesignParameters, DesignCandidate
from ..schemas.ml import MLPredictRequest, MLPredictResponse, MLStatusResponse
from ..schemas.optimization import OptimizationRequest, OptimizationResponse
from ..schemas.simulation import SimulationRunRequest, SimulationRunResponse, ValidationRunResponse
from ..schemas.agent import AgentRunRequest, AgentRunResponse
from ..schemas.report import ReportGenerateRequest, ReportGenerateResponse

from ..services.climate_service import climate_service
from ..services.soil_service import soil_service
from ..services.env_profile_service import env_profile_service
from ..services.material_service import material_service
from ..services.design_service import design_service
from ..services.ml_service import ml_service
from ..services.optimization_service import optimization_service
from ..services.ansys_service import ansys_service
from ..services.validation_service import validation_service
from ..services.agent_service import agent_service
from ..services.report_service import report_service

router = APIRouter()

# Health
@router.get("/health")
def health_check():
    return {
        "status": "online",
        "service": "ClimateShelter AI Backend",
        "version": "1.0.0",
        "demo_mode": True
    }

# Location
@router.post("/location", response_model=LocationSearchResponse)
def search_location(query: LocationQuery):
    results = climate_service.search_location(query.query)
    model_results = [LocationSearchResult(**r) for r in results]
    return LocationSearchResponse(results=model_results, source="LIVE" if results else "SAMPLE")

# Climate
@router.post("/climate")
def get_climate(req: EnvProfileRequest):
    return climate_service.get_climate_data(req.latitude, req.longitude)

# Soil
@router.post("/soil")
def get_soil(req: EnvProfileRequest):
    return soil_service.get_soil_data(req.latitude, req.longitude)

# Environmental Profile
@router.post("/environment/profile", response_model=EnvironmentalProfile)
def get_environment_profile(req: EnvProfileRequest):
    return env_profile_service.create_profile(req.latitude, req.longitude, req.location_name)

# Materials
@router.get("/materials", response_model=List[Material])
def get_materials():
    return material_service.get_all_materials()

@router.post("/materials/compare")
def compare_materials(req: EnvProfileRequest):
    env = env_profile_service.create_profile(req.latitude, req.longitude, req.location_name)
    items = material_service.compare_all_materials(env)
    return {
        "location_name": env.location_name,
        "outdoor_avg_temp": env.average_temperature,
        "materials": items
    }


# Candidates
@router.post("/design/candidates")
def generate_candidates(req: EnvProfileRequest):
    env = env_profile_service.create_profile(req.latitude, req.longitude, req.location_name)
    opt_req = OptimizationRequest(environment=env)
    opt_res = optimization_service.run_optimization(opt_req)
    return {
        "best_design": opt_res.best_design,
        "candidates": [opt_res.best_design] + opt_res.alternatives
    }

# ML Status
@router.get("/ml/status", response_model=MLStatusResponse)
def get_ml_status():
    return ml_service.get_status()

# ML Train
@router.post("/ml/train")
def train_ml_model():
    return ml_service.train_model()

# ML Predict
@router.post("/ml/predict", response_model=MLPredictResponse)
def predict_ml(req: MLPredictRequest):
    return ml_service.predict_interior_temperature(req.design, req.environment)

# Optimization Run
@router.post("/optimization/run", response_model=OptimizationResponse)
def run_optimization(req: OptimizationRequest):
    return optimization_service.run_optimization(req)

# Simulation Run
@router.post("/simulation/run", response_model=SimulationRunResponse)
def run_simulation(req: SimulationRunRequest):
    return ansys_service.run_simulation(req.design, req.environment)

# Validation Run
@router.post("/validation/run", response_model=ValidationRunResponse)
def run_validation(req: SimulationRunRequest):
    return validation_service.validate_design(req.design, req.environment)

# Agent Run
@router.post("/agent/run", response_model=AgentRunResponse)
def run_agent(req: AgentRunRequest):
    return agent_service.run_agent(req)

# Multi-site profile endpoint
@router.post("/environment/multi-profile")
def get_multi_environment_profiles(req: Dict[str, Any]):
    sites = req.get("sites", [])
    profiles = env_profile_service.create_multi_profiles(sites)
    return {"profiles": profiles}

# Multi-site optimization comparison endpoint
@router.post("/optimization/multi-site")
def run_multi_site_optimization(req: Dict[str, Any]):
    sites = req.get("sites", [])
    priority = req.get("priority", "thermal_comfort")
    return optimization_service.run_multi_site_optimization(sites, priority)

# Report Generate
@router.post("/report/generate", response_model=ReportGenerateResponse)
def generate_report(req: ReportGenerateRequest):
    res = report_service.generate_report(req.location_name, req.latitude, req.longitude)
    return ReportGenerateResponse(**res)

