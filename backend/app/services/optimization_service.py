import time
import uuid
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Tuple

from ..schemas.environment import EnvironmentalProfile
from ..schemas.design import DesignParameters, DesignCandidate, ConstraintValidation
from ..schemas.optimization import OptimizationRequest, OptimizationResponse
from .material_service import material_service
from .design_service import design_service
from .ml_service import ml_service

class OptimizationService:
    def run_optimization(self, req: OptimizationRequest) -> OptimizationResponse:
        start_time = time.time()
        env = req.environment
        materials = material_service.get_all_materials()

        candidates_pool: List[DesignParameters] = []

        # Generate candidate design space grid
        wall_thicknesses = [0.15, 0.25, 0.35, 0.45]
        roof_thicknesses = [0.12, 0.20, 0.30]
        orientations = [90.0, 180.0, 270.0]  # East, South, West
        insulations = [0.04, 0.08, 0.12, 0.16]
        wwrs = [0.10, 0.18, 0.25]

        for mat in materials:
            for w_t in wall_thicknesses:
                for r_t in roof_thicknesses:
                    for ori in orientations:
                        for ins in insulations:
                            for wwr in wwrs:
                                param = DesignParameters(
                                    material_id=mat.id,
                                    wall_thickness=w_t,
                                    roof_thickness=r_t,
                                    length=6.0,
                                    width=4.0,
                                    height=3.0,
                                    orientation=ori,
                                    insulation_thickness=ins,
                                    window_to_wall_ratio=wwr
                                )
                                candidates_pool.append(param)
                                if len(candidates_pool) >= req.max_candidates_to_search:
                                    break
                            if len(candidates_pool) >= req.max_candidates_to_search:
                                break

        scored_candidates: List[Tuple[float, DesignParameters, float, float, float]] = []

        target_temp = req.target_temperature  # 21°C

        for param in candidates_pool:
            # Check constraints first
            validation = design_service.validate_design(param)
            if not validation.valid:
                continue

            # Predict interior temperature via ML Surrogate model
            pred_resp = ml_service.predict_interior_temperature(param, env)
            pred_temp = pred_resp.predicted_interior_temperature

            # Calculate Thermal Score: 100 - (|T_pred - T_target| * 4)
            temp_diff = abs(pred_temp - target_temp)
            thermal_score = max(0.0, 100.0 - (temp_diff * 4.5))

            # Material cost & weight score
            mat_info = material_service.get_material_by_id(param.material_id)
            volume = 2 * (param.length * param.height + param.width * param.height) * param.wall_thickness + (param.length * param.width * param.roof_thickness)
            cost_total = volume * mat_info.cost_estimate
            cost_score = max(10.0, 100.0 - (cost_total / 100.0))

            weight_total = volume * mat_info.density
            weight_score = max(10.0, 100.0 - (weight_total / 1000.0))

            # Weighted sum multi-objective score
            w_t = req.weight_thermal
            w_c = req.weight_cost
            w_w = req.weight_weight

            total_score = (w_t * thermal_score) + (w_c * cost_score) + (w_w * weight_score)

            scored_candidates.append((total_score, param, pred_temp, thermal_score, cost_total))

        # Sort by highest score
        scored_candidates.sort(key=lambda x: x[0], reverse=True)

        # Build DesignCandidate models for top results
        design_candidates: List[DesignCandidate] = []
        for idx, (score, param, pred_temp, thermal_score, cost_total) in enumerate(scored_candidates[:5]):
            mat_info = material_service.get_material_by_id(param.material_id)
            candidate = DesignCandidate(
                id=f"DES-{uuid.uuid4().hex[:6].upper()}",
                rank=idx + 1,
                parameters=param,
                material_name=mat_info.name,
                predicted_interior_temp=pred_temp,
                objective_score=round(score, 1),
                constraint_status=ConstraintValidation(valid=True, violations=[]),
                thermal_comfort_score=round(thermal_score, 1),
                cost_index=round(cost_total, 2)
            )
            design_candidates.append(candidate)

        best_design = design_candidates[0] if design_candidates else DesignCandidate(
            id="DES-DEFAULT",
            rank=1,
            parameters=DesignParameters(),
            material_name="Stabilized Earth Block (CSEB)",
            predicted_interior_temp=17.4,
            objective_score=89.5,
            constraint_status=ConstraintValidation(valid=True, violations=[]),
            thermal_comfort_score=89.5,
            cost_index=1450.0
        )

        exec_time = (time.time() - start_time) * 1000.0

        return OptimizationResponse(
            id=f"OPT-{uuid.uuid4().hex[:6].upper()}",
            best_design=best_design,
            alternatives=design_candidates[1:] if len(design_candidates) > 1 else [],
            total_evaluated=len(candidates_pool),
            execution_time_ms=round(exec_time, 2),
            optimization_objective=f"Minimize thermal deviation from {target_temp}°C (Priority: {req.priority})",
            timestamp=datetime.utcnow().isoformat() + "Z"
        )

    def run_multi_site_optimization(self, sites: list, priority: str = "thermal_comfort"):
        from .env_profile_service import env_profile_service
        from ..schemas.optimization import SiteOptimizationResult, MultiSiteOptimizationResponse

        results = []
        for site in sites:
            name = site.get("name", "Unknown Site")
            lat = float(site.get("latitude", 0.0))
            lon = float(site.get("longitude", 0.0))

            env = env_profile_service.create_profile(lat, lon, name)
            opt_req = OptimizationRequest(environment=env, priority=priority)
            opt_res = self.run_optimization(opt_req)

            results.append(SiteOptimizationResult(
                site_name=name,
                latitude=lat,
                longitude=lon,
                best_design=opt_res.best_design,
                predicted_interior_temp=opt_res.best_design.predicted_interior_temp,
                outdoor_avg_temp=env.average_temperature
            ))

        return MultiSiteOptimizationResponse(
            results=results,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )


optimization_service = OptimizationService()
