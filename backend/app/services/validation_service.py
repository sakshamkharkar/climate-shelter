import uuid
from datetime import datetime
from ..schemas.design import DesignParameters
from ..schemas.environment import EnvironmentalProfile
from ..schemas.simulation import ValidationRunResponse
from .ml_service import ml_service
from .ansys_service import ansys_service

class ValidationService:
    def validate_design(
        self,
        design: DesignParameters,
        env: EnvironmentalProfile
    ) -> ValidationRunResponse:
        # 1. Predict with ML Surrogate
        ml_res = ml_service.predict_interior_temperature(design, env)
        t_ml = ml_res.predicted_interior_temperature

        # 2. Run High-Fidelity ANSYS Simulation
        ansys_res = ansys_service.run_simulation(design, env)
        t_ansys = ansys_res.interior_temperature

        # 3. Calculate Error
        abs_err = round(abs(t_ml - t_ansys), 2)
        rel_err = round((abs_err / max(0.1, abs(t_ansys))) * 100.0, 2)

        # Validation passes if error is under 5% or 1.5°C threshold
        passed = abs_err <= 1.5 or rel_err <= 5.0

        return ValidationRunResponse(
            validation_id=f"VAL-{uuid.uuid4().hex[:6].upper()}",
            design_id=f"DES-{uuid.uuid4().hex[:4].upper()}",
            ml_prediction_temp=t_ml,
            ansys_simulation_temp=t_ansys,
            absolute_error=abs_err,
            relative_error_percentage=rel_err,
            model_version=ml_res.model_version,
            ansys_mode=ansys_res.ansys_mode,
            passed_validation=passed,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )

validation_service = ValidationService()
