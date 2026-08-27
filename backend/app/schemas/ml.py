from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from .design import DesignParameters
from .environment import EnvironmentalProfile

class MLPredictRequest(BaseModel):
    design: DesignParameters
    environment: EnvironmentalProfile

class MLPredictResponse(BaseModel):
    predicted_interior_temperature: float
    model_version: str
    model_type: str
    domain_warning: bool
    domain_warning_message: Optional[str] = None
    confidence_interval: Optional[Dict[str, float]] = None

class MLMetrics(BaseModel):
    mae: float
    rmse: float
    r2: float
    model_name: str
    dataset_size: int
    training_samples: int
    validation_samples: int
    test_samples: int
    feature_count: int
    features: List[str]
    target: str = "interior_temperature"
    training_date: str

class MLStatusResponse(BaseModel):
    status: str  # TRAINED, UNTRAINED, MOCK
    active_model: str
    metrics: Optional[MLMetrics] = None
    available_models: List[str] = Field(default_factory=list)
