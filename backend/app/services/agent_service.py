import time
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from ..schemas.agent import AgentRunRequest, AgentRunResponse, ToolCallLog
from ..schemas.design import DesignParameters
from ..schemas.optimization import OptimizationRequest
from .climate_service import climate_service
from .soil_service import soil_service
from .env_profile_service import env_profile_service
from .material_service import material_service
from .design_service import design_service
from .ml_service import ml_service
from .optimization_service import optimization_service
from .validation_service import validation_service
from .report_service import report_service

logger = logging.getLogger(__name__)

class AgentService:
    def run_agent(self, req: AgentRunRequest) -> AgentRunResponse:
        tool_logs: List[ToolCallLog] = []
        now_str = datetime.utcnow().strftime("%H:%M:%S")

        # 1. Geocode Location Tool
        loc_query = req.location_name or "Leh, Ladakh"
        tool_logs.append(ToolCallLog(
            tool_name="get_location",
            arguments={"query": loc_query},
            output={"status": "success", "query": loc_query, "latitude": req.latitude, "longitude": req.longitude},
            timestamp=now_str
        ))

        # 2. Get Climate & Soil Profile Tool
        lat = req.latitude or 34.1526
        lon = req.longitude or 77.5771
        env = env_profile_service.create_profile(lat, lon, loc_query)
        tool_logs.append(ToolCallLog(
            tool_name="create_environment_profile",
            arguments={"latitude": lat, "longitude": lon, "location_name": loc_query},
            output={
                "status": "success",
                "location": env.location_name,
                "avg_temp": env.average_temperature,
                "solar_radiation": env.solar_radiation,
                "humidity": env.humidity,
                "soil_type": env.soil_properties.soil_type,
                "source": env.data_source
            },
            timestamp=now_str
        ))

        # 3. Materials Tool
        materials = material_service.get_all_materials()
        tool_logs.append(ToolCallLog(
            tool_name="get_materials",
            arguments={"count": len(materials)},
            output={"status": "success", "available_materials": [m.name for m in materials]},
            timestamp=now_str
        ))

        # 4. Optimization Tool
        opt_req = OptimizationRequest(
            environment=env,
            target_temperature=21.0,
            priority="thermal_comfort"
        )
        opt_res = optimization_service.run_optimization(opt_req)
        best = opt_res.best_design
        tool_logs.append(ToolCallLog(
            tool_name="optimize_design",
            arguments={"priority": "thermal_comfort", "candidates_evaluated": opt_res.total_evaluated},
            output={
                "status": "success",
                "best_design_id": best.id,
                "material": best.material_name,
                "predicted_interior_temp": best.predicted_interior_temp,
                "objective_score": best.objective_score
            },
            timestamp=now_str
        ))

        # 5. Validation Tool
        val_res = validation_service.validate_design(best.parameters, env)
        tool_logs.append(ToolCallLog(
            tool_name="validate_design",
            arguments={"design_id": best.id},
            output={
                "status": "success",
                "ml_temp": val_res.ml_prediction_temp,
                "ansys_temp": val_res.ansys_simulation_temp,
                "absolute_error": val_res.absolute_error,
                "passed": val_res.passed_validation,
                "ansys_mode": val_res.ansys_mode
            },
            timestamp=now_str
        ))

        # Generate Explainable Natural Language Recommendation
        explanation = (
            f"### ClimateShelter AI — Decision Support Recommendation\n\n"
            f"Based on the environmental profile for **{env.location_name}** (Avg Temp: {env.average_temperature}°C, "
            f"Solar Irradiance: {env.solar_radiation} W/m², Soil: {env.soil_properties.soil_type}), the optimization engine "
            f"evaluated {opt_res.total_evaluated} candidate designs and selected **{best.material_name}** as the optimal wall construction.\n\n"
            f"**Key Design Specifications:**\n"
            f"- **Wall Thickness**: {best.parameters.wall_thickness:.2f} m\n"
            f"- **Roof Thickness**: {best.parameters.roof_thickness:.2f} m\n"
            f"- **Orientation**: {best.parameters.orientation:.0f}° South-Facing\n"
            f"- **Insulation Thickness**: {best.parameters.insulation_thickness:.3f} m\n"
            f"- **Predicted Interior Temperature**: **{best.predicted_interior_temp:.1f}°C**\n\n"
            f"**Engineering Validation:**\n"
            f"- ANSYS Simulation Result: **{val_res.ansys_simulation_temp:.1f}°C**\n"
            f"- Prediction Absolute Error: **{val_res.absolute_error:.2f}°C** ({val_res.relative_error_percentage:.1f}%)\n"
            f"- Validation Status: **{'Passed' if val_res.passed_validation else 'Needs Review'}** (`{val_res.ansys_mode}` mode)\n\n"
            f"**Why this design?**\n"
            f"The high thermal mass of {best.material_name} dampens ambient diurnal fluctuations, while the South orientation captures "
            f"maximum solar radiation. The {best.parameters.insulation_thickness * 100:.0f}cm insulation layer prevents nighttime heat dissipation."
        )

        return AgentRunResponse(
            response=explanation,
            tool_calls=tool_logs,
            recommended_design=best.dict(),
            environmental_summary=env.dict(),
            validation_summary=val_res.dict()
        )

agent_service = AgentService()
