from typing import List, Dict, Any
from ..schemas.design import DesignParameters, ConstraintValidation
from .material_service import material_service

class DesignService:
    def validate_design(self, design: DesignParameters) -> ConstraintValidation:
        violations = []

        if design.wall_thickness < 0.05 or design.wall_thickness > 1.0:
            violations.append("Wall thickness must be between 0.05m and 1.0m")

        if design.roof_thickness < 0.05 or design.roof_thickness > 0.8:
            violations.append("Roof thickness must be between 0.05m and 0.8m")

        if design.length < 2.0 or design.length > 20.0:
            violations.append("Building length must be between 2.0m and 20.0m")

        if design.width < 2.0 or design.width > 20.0:
            violations.append("Building width must be between 2.0m and 20.0m")

        if design.height < 2.0 or design.height > 6.0:
            violations.append("Building height must be between 2.0m and 6.0m")

        if design.orientation < 0.0 or design.orientation > 360.0:
            violations.append("Orientation must be between 0° and 360°")

        if design.insulation_thickness < 0.0 or design.insulation_thickness > 0.35:
            violations.append("Insulation thickness must be between 0.0m and 0.35m")

        if design.window_to_wall_ratio < 0.0 or design.window_to_wall_ratio > 0.60:
            violations.append("Window-to-wall ratio must be between 0.0 and 0.60")

        # Material check
        mat = material_service.get_material_by_id(design.material_id)
        if not mat:
            violations.append(f"Invalid material selection: {design.material_id}")

        return ConstraintValidation(
            valid=len(violations) == 0,
            violations=violations
        )

design_service = DesignService()
