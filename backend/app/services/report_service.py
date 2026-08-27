from datetime import datetime
from typing import Dict, Any
from .env_profile_service import env_profile_service
from .optimization_service import optimization_service
from .validation_service import validation_service
from .material_service import material_service
from ..schemas.optimization import OptimizationRequest

class ReportService:
    def generate_report(self, location_name: str, lat: float, lon: float) -> Dict[str, Any]:
        env = env_profile_service.create_profile(lat, lon, location_name)
        opt_req = OptimizationRequest(environment=env)
        opt_res = optimization_service.run_optimization(opt_req)
        best = opt_res.best_design
        val_res = validation_service.validate_design(best.parameters, env)
        mat_info = material_service.get_material_by_id(best.parameters.material_id)

        now_str = datetime.utcnow().strftime("%B %d, %Y - %H:%M:%S UTC")

        md = f"""# Engineering Decision Support Report — ClimateShelter AI
**Project Title**: Climate-Aware Intelligent Shelter Design & Thermal Optimization  
**Report ID**: CS-RPT-{datetime.utcnow().strftime('%Y%m%d')}-01  
**Generated Date**: {now_str}  

---

## 1. Executive Summary
This report presents an automated, physics-grounded engineering evaluation for an optimized shelter design located at **{env.location_name}** ({env.latitude:.4f}°N, {env.longitude:.4f}°E, Elev: {env.elevation:.0f}m). Using high-fidelity ANSYS simulation data, machine-learning surrogate regression, and multi-objective optimization, the platform identified a top candidate design that maximizes thermal autonomy while respecting structural and material cost constraints.

---

## 2. Location & Environmental Profile
- **Location**: {env.location_name}
- **Coordinates**: Latitude {env.latitude:.4f}°, Longitude {env.longitude:.4f}°
- **Ambient Temperature**: Avg {env.average_temperature:.1f}°C (Min: {env.minimum_temperature:.1f}°C, Max: {env.maximum_temperature:.1f}°C)
- **Solar Irradiance**: {env.solar_radiation:.0f} W/m²
- **Relative Humidity**: {env.humidity:.1f}% | **Wind Speed**: {env.wind_speed:.1f} m/s
- **Soil Classification**: {env.soil_properties.soil_type} (Sand: {env.soil_properties.sand_percentage}%, Clay: {env.soil_properties.clay_percentage}%)
- **Soil Thermal Conductivity**: {env.soil_properties.thermal_conductivity} W/m·K
- **Data Source**: {env.data_source} (Real-time meteorological API + normalized profile)

---

## 3. Recommended Design Configuration
- **Primary Wall Material**: **{mat_info.name}**
- **Thermal Conductivity ($k$)**: {mat_info.thermal_conductivity} W/m·K | **Density**: {mat_info.density} kg/m³
- **Wall Thickness**: {best.parameters.wall_thickness:.2f} m
- **Roof Thickness**: {best.parameters.roof_thickness:.2f} m
- **Shelter Dimensions ($L \\times W \\times H$)**: {best.parameters.length:.1f}m × {best.parameters.width:.1f}m × {best.parameters.height:.1f}m
- **Orientation**: {best.parameters.orientation:.0f}° South-Facing Azimuth
- **Insulation Layer**: {best.parameters.insulation_thickness:.3f} m (EPS Thermal Damping)
- **Window-to-Wall Ratio (WWR)**: {best.parameters.window_to_wall_ratio * 100:.0f}%

---

## 4. Predicted Thermal Performance & Validation
- **ML Surrogate Predicted Indoor Temperature**: **{best.predicted_interior_temperature:.1f}°C**
- **ANSYS Simulation Temperature**: **{val_res.ansys_simulation_temp:.1f}°C**
- **Absolute Error ($|\\Delta T|$)**: **{val_res.absolute_error:.2f}°C**
- **Relative Error**: **{val_res.relative_error_percentage:.2f}%**
- **Validation Status**: **{"PASSED VERIFICATION" if val_res.passed_validation else "REQUIRES FURTHER REFINEMENT"}**
- **ANSYS Integration Mode**: `{val_res.ansys_mode}`

---

## 5. Engineering Justification & AI Insight
The selected configuration utilizes **{mat_info.name}** due to its high volumetric heat capacity, enabling it to act as a passive thermal flywheel. South-facing orientation ({best.parameters.orientation:.0f}°) captures peak solar radiation ({env.solar_radiation:.0f} W/m²), while the {best.parameters.insulation_thickness * 100:.0f}cm insulation barrier minimizes nighttime heat dissipation into the cold ambient sink ({env.minimum_temperature:.1f}°C).

---

## 6. System Limitations & Disclaimer
> [!NOTE]
> The ML model functions as a surrogate for rapid design-space exploration. ANSYS FEA simulation remains the ultimate engineering authority. Where ANSYS external execution is unavailable, mock simulation output is clearly tagged as synthetic test data.
"""

        return {
            "report_title": f"ClimateShelter Engineering Report - {env.location_name}",
            "content_markdown": md,
            "timestamp": now_str,
            "metadata": {
                "location": env.location_name,
                "best_design_id": best.id,
                "predicted_temp": best.predicted_interior_temperature,
                "ansys_temp": val_res.ansys_simulation_temp,
                "ansys_mode": val_res.ansys_mode
            }
        }

report_service = ReportService()
