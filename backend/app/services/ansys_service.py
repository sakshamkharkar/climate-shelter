from typing import Dict, Any
from ..config import settings
from ..integrations.ansys_provider import PyMAPDLProvider, MockANSYSProvider, ANSYSProvider
from ..schemas.design import DesignParameters
from ..schemas.environment import EnvironmentalProfile
from ..schemas.simulation import SimulationRunResponse
from .material_service import material_service

class ANSYSService:
    def __init__(self):
        if settings.ANSYS_MODE == "pymapdl":
            self.provider: ANSYSProvider = PyMAPDLProvider(settings.ANSYS_EXECUTABLE_PATH)
        else:
            self.provider: ANSYSProvider = MockANSYSProvider()

    def run_simulation(
        self,
        design: DesignParameters,
        env: EnvironmentalProfile
    ) -> SimulationRunResponse:
        mat_info = material_service.get_material_by_id(design.material_id)

        design_dict = design.dict()
        design_dict["thermal_conductivity"] = mat_info.thermal_conductivity
        design_dict["density"] = mat_info.density
        design_dict["specific_heat"] = mat_info.specific_heat

        env_dict = env.dict()

        res = self.provider.run_simulation(design_dict, env_dict)

        return SimulationRunResponse(
            simulation_id=res["simulation_id"],
            ansys_mode=res["ansys_mode"],
            status=res["status"],
            interior_temperature=res["interior_temperature"],
            max_surface_temp=res["max_surface_temp"],
            min_surface_temp=res["min_surface_temp"],
            total_heat_flux=res["total_heat_flux"],
            execution_time_seconds=res["execution_time_seconds"],
            apdl_script_preview=res["apdl_script_preview"],
            data_source_label=res["data_source_label"],
            timestamp=env.timestamp
        )

ansys_service = ANSYSService()
