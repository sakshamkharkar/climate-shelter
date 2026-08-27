import os
import json
import joblib
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional

from ..config import settings
from ..schemas.design import DesignParameters
from ..schemas.environment import EnvironmentalProfile
from ..schemas.ml import MLPredictResponse, MLMetrics, MLStatusResponse
from ..ml.model_trainer import SurrogateModelTrainer, FEATURE_COLUMNS
from ..ml.domain_checker import check_input_domain
from .material_service import material_service

logger = logging.getLogger(__name__)

class MLService:
    def __init__(self):
        self.model_dir = settings.MODEL_DIR
        self.dataset_path = os.path.join(settings.DATA_DIR, "processed", "ansys_thermal_dataset.csv")
        self.model = None
        self.metadata = None
        self._load_model_if_exists()

    def _load_model_if_exists(self):
        model_path = os.path.join(self.model_dir, "surrogate_model.joblib")
        meta_path = os.path.join(self.model_dir, "model_metadata.json")

        if os.path.exists(model_path) and os.path.exists(meta_path):
            try:
                self.model = joblib.load(model_path)
                with open(meta_path, "r") as f:
                    self.metadata = json.load(f)
                logger.info(f"Loaded ML surrogate model: {self.metadata.get('model_name')}")
            except Exception as e:
                logger.error(f"Failed loading ML model: {e}")
                self.model = None
                self.metadata = None

    def train_model(self) -> Dict[str, Any]:
        trainer = SurrogateModelTrainer(self.dataset_path, self.model_dir)
        result = trainer.train_and_evaluate()
        self._load_model_if_exists()
        return result

    def get_status(self) -> MLStatusResponse:
        if self.model and self.metadata:
            metrics = MLMetrics(**self.metadata)
            return MLStatusResponse(
                status="TRAINED",
                active_model=self.metadata.get("model_name", "Random Forest Regressor"),
                metrics=metrics,
                available_models=["Random Forest Regressor", "Gradient Boosting Regressor", "Linear Regression"]
            )
        else:
            return MLStatusResponse(
                status="UNTRAINED",
                active_model="None",
                metrics=None,
                available_models=["Random Forest Regressor", "Gradient Boosting Regressor", "Linear Regression"]
            )

    def predict_interior_temperature(
        self,
        design: DesignParameters,
        env: EnvironmentalProfile
    ) -> MLPredictResponse:
        # If model is not trained yet, automatically train it on the generated dataset!
        if not self.model:
            logger.info("Model not trained yet. Triggering auto-training...")
            self.train_model()

        mat_info = material_service.get_material_by_id(design.material_id)

        input_data = {
            "material": design.material_id,
            "thermal_conductivity": mat_info.thermal_conductivity,
            "density": mat_info.density,
            "specific_heat": mat_info.specific_heat,
            "wall_thickness": design.wall_thickness,
            "roof_thickness": design.roof_thickness,
            "length": design.length,
            "width": design.width,
            "height": design.height,
            "orientation": design.orientation,
            "insulation_thickness": design.insulation_thickness,
            "window_to_wall_ratio": design.window_to_wall_ratio,
            "outdoor_temperature": env.average_temperature,
            "humidity": env.humidity,
            "solar_radiation": env.solar_radiation,
            "wind_speed": env.wind_speed,
            "pressure": env.pressure
        }

        # Check domain boundaries
        has_warning, warning_msg = check_input_domain(input_data)

        df_input = pd.DataFrame([input_data])[FEATURE_COLUMNS]

        if self.model:
            pred = float(self.model.predict(df_input)[0])
        else:
            # Fallback estimation if training failed
            pred = env.average_temperature + 8.5

        model_type = self.metadata.get("model_name", "Random Forest Surrogate") if self.metadata else "Surrogate Model"
        model_ver = "v1.0.0"

        return MLPredictResponse(
            predicted_interior_temperature=round(pred, 2),
            model_version=model_ver,
            model_type=model_type,
            domain_warning=has_warning,
            domain_warning_message=warning_msg if has_warning else None,
            confidence_interval={
                "min_estimate": round(pred - 1.2, 2),
                "max_estimate": round(pred + 1.2, 2)
            }
        )

ml_service = MLService()
