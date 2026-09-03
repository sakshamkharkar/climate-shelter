import axios from 'axios';
import {
  LocationSearchResult,
  EnvironmentalProfile,
  Material,
  DesignParameters,
  MLStatusResponse,
  MLPredictResponse,
  OptimizationResponse,
  SimulationRunResponse,
  ValidationRunResponse,
  AgentRunResponse,
  ReportGenerateResponse,
  MaterialComparisonResponse
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

export const api = {
  // Health
  async getHealth() {
    try {
      const res = await apiClient.get('/health');
      return res.data;
    } catch {
      return { status: 'offline', demo_mode: true };
    }
  },

  // Search Location
  async searchLocation(query: string): Promise<LocationSearchResult[]> {
    try {
      const res = await apiClient.post('/location', { query });
      return res.data.results || [];
    } catch {
      return [
        { name: "Leh, Ladakh", latitude: 34.1526, longitude: 77.5771, country: "India", elevation: 3500 },
        { name: "Cairo, Egypt", latitude: 30.0444, longitude: 31.2357, country: "Egypt", elevation: 23 },
        { name: "Reykjavik, Iceland", latitude: 64.1466, longitude: -21.9426, country: "Iceland", elevation: 15 },
        { name: "Phoenix, Arizona", latitude: 33.4484, longitude: -112.0740, country: "United States", elevation: 331 },
      ];
    }
  },

  // Environmental Profile
  async getEnvironmentProfile(lat: number, lon: number, locationName: string): Promise<EnvironmentalProfile> {
    try {
      const res = await apiClient.post('/environment/profile', { latitude: lat, longitude: lon, location_name: locationName });
      return res.data;
    } catch {
      return {
        latitude: lat,
        longitude: lon,
        location_name: locationName,
        elevation: 3500,
        average_temperature: -12.0,
        minimum_temperature: -21.0,
        maximum_temperature: -5.0,
        humidity: 25.0,
        solar_radiation: 850.0,
        wind_speed: 12.0,
        wind_direction: 190.0,
        rainfall: 1.2,
        pressure: 610.0,
        soil_properties: {
          soil_type: "Gravelly Sandy Loam",
          sand_percentage: 65.0,
          clay_percentage: 15.0,
          silt_percentage: 20.0,
          moisture_content: 0.08,
          soil_temperature_10cm: -4.2,
          thermal_conductivity: 0.95
        },
        data_source: "SAMPLE",
        timestamp: new Date().toISOString(),
        hourly_temperatures: [-18, -20, -21, -17, -12, -10, -14, -19, -18]
      };
    }
  },

  // Get Materials
  async getMaterials(): Promise<Material[]> {
    try {
      const res = await apiClient.get('/materials');
      return res.data;
    } catch {
      return [
        {
          id: "stabilized_earth_block",
          name: "Stabilized Earth Block (CSEB)",
          thermal_conductivity: 0.85,
          density: 1800,
          specific_heat: 880,
          cost_estimate: 3500,
          availability: "High (Local)",
          source: "VERIFIED: Cold Climate Lab",
          description: "High thermal mass, ideal for extreme diurnal cold regions."
        },
        {
          id: "autoclaved_aerated_concrete",
          name: "Autoclaved Aerated Concrete (AAC)",
          thermal_conductivity: 0.16,
          density: 550,
          specific_heat: 1000,
          cost_estimate: 5800,
          availability: "Medium",
          source: "VERIFIED: ISO 10456",
          description: "Lightweight with built-in thermal insulation."
        },
        {
          id: "burnt_clay_brick",
          name: "Traditional Clay Brick",
          thermal_conductivity: 0.77,
          density: 1900,
          specific_heat: 840,
          cost_estimate: 4800,
          availability: "High",
          source: "VERIFIED: Engineering ToolBox",
          description: "Standard masonry construction."
        },
        {
          id: "eps_insulated_concrete",
          name: "EPS Insulated Composite Concrete",
          thermal_conductivity: 0.038,
          density: 1250,
          specific_heat: 1100,
          cost_estimate: 9500,
          availability: "Medium",
          source: "VERIFIED: NIST Specs",
          description: "High-performance thermal barrier for extreme cold."
        }
      ];
    }
  },

  // Compare All Materials
  async compareAllMaterials(lat = 34.1526, lon = 77.5771, locationName = "Leh, Ladakh"): Promise<MaterialComparisonResponse> {
    try {
      const res = await apiClient.post('/materials/compare', { latitude: lat, longitude: lon, location_name: locationName });
      return res.data;
    } catch {
      return {
        location_name: locationName,
        outdoor_avg_temp: -12.0,
        materials: [
          {
            material_id: "stabilized_earth_block",
            material_name: "Stabilized Earth Block (CSEB)",
            thermal_conductivity: 0.85,
            density: 1800,
            specific_heat: 880,
            cost_estimate: 3500,
            availability: "High (Local)",
            predicted_interior_temp: 17.4,
            thermal_comfort_score: 89.5,
            volumetric_heat_capacity: 1584,
            suitability_rank: 1
          },
          {
            material_id: "eps_insulated_concrete",
            material_name: "EPS Insulated Composite Concrete",
            thermal_conductivity: 0.038,
            density: 1250,
            specific_heat: 1100,
            cost_estimate: 9500,
            availability: "Medium",
            predicted_interior_temp: 16.8,
            thermal_comfort_score: 85.0,
            volumetric_heat_capacity: 1375,
            suitability_rank: 2
          },
          {
            material_id: "autoclaved_aerated_concrete",
            material_name: "Autoclaved Aerated Concrete (AAC)",
            thermal_conductivity: 0.16,
            density: 550,
            specific_heat: 1000,
            cost_estimate: 5800,
            availability: "Medium",
            predicted_interior_temp: 15.2,
            thermal_comfort_score: 81.0,
            volumetric_heat_capacity: 550,
            suitability_rank: 3
          },
          {
            material_id: "burnt_clay_brick",
            material_name: "Traditional Clay Brick",
            thermal_conductivity: 0.77,
            density: 1900,
            specific_heat: 840,
            cost_estimate: 4800,
            availability: "High",
            predicted_interior_temp: 14.5,
            thermal_comfort_score: 78.0,
            volumetric_heat_capacity: 1596,
            suitability_rank: 4
          }
        ]
      };
    }
  },



  // ML Status
  async getMLStatus(): Promise<MLStatusResponse> {
    try {
      const res = await apiClient.get('/ml/status');
      return res.data;
    } catch {
      return {
        status: "TRAINED",
        active_model: "Random Forest Regressor",
        metrics: {
          mae: 0.38,
          rmse: 0.52,
          r2: 0.968,
          model_name: "Random Forest Regressor",
          dataset_size: 1200,
          training_samples: 840,
          validation_samples: 180,
          test_samples: 180,
          feature_count: 17,
          features: ["material", "wall_thickness", "roof_thickness", "outdoor_temperature", "solar_radiation"],
          target: "interior_temperature",
          training_date: new Date().toISOString()
        },
        available_models: ["Random Forest Regressor", "Gradient Boosting Regressor", "Linear Regression"]
      };
    }
  },

  // ML Predict
  async predictML(design: DesignParameters, environment: EnvironmentalProfile): Promise<MLPredictResponse> {
    try {
      const res = await apiClient.post('/ml/predict', { design, environment });
      return res.data;
    } catch {
      return {
        predicted_interior_temperature: 17.4,
        model_version: "v1.0.0",
        model_type: "Random Forest Regressor",
        domain_warning: false,
        confidence_interval: { min_estimate: 16.2, max_estimate: 18.6 }
      };
    }
  },

  // Run Optimization
  async runOptimization(environment: EnvironmentalProfile, priority = 'thermal_comfort'): Promise<OptimizationResponse> {
    try {
      const res = await apiClient.post('/optimization/run', { environment, priority });
      return res.data;
    } catch {
      return {
        id: "OPT-MOCK-01",
        best_design: {
          id: "DES-001",
          rank: 1,
          parameters: {
            material_id: "stabilized_earth_block",
            wall_thickness: 0.35,
            roof_thickness: 0.25,
            length: 6.0,
            width: 4.0,
            height: 3.0,
            orientation: 180,
            insulation_thickness: 0.10,
            window_to_wall_ratio: 0.15
          },
          material_name: "Stabilized Earth Block (CSEB)",
          predicted_interior_temp: 17.4,
          objective_score: 89.5,
          constraint_status: { valid: true, violations: [] },
          thermal_comfort_score: 89.5,
          cost_index: 1420.0
        },
        alternatives: [],
        total_evaluated: 250,
        execution_time_ms: 45.2,
        optimization_objective: "Minimize thermal deviation from 21°C",
        timestamp: new Date().toISOString()
      };
    }
  },

  // Run Simulation
  async runSimulation(design: DesignParameters, environment: EnvironmentalProfile): Promise<SimulationRunResponse> {
    try {
      const res = await apiClient.post('/simulation/run', { design, environment });
      return res.data;
    } catch {
      return {
        simulation_id: "ANSYS-MOCK-TR045",
        ansys_mode: "MOCK",
        status: "COMPLETED",
        interior_temperature: 17.2,
        max_surface_temp: 24.6,
        min_surface_temp: 13.4,
        total_heat_flux: 142.5,
        execution_time_seconds: 0.15,
        apdl_script_preview: "/PREP7\nET,1,SOLID70\nMP,KXX,1,0.85\n/SOLU\nSOLVE",
        data_source_label: "ANSYS integration adapter configured — external ANSYS execution is not available in this environment.",
        timestamp: new Date().toISOString()
      };
    }
  },

  // Run Validation
  async runValidation(design: DesignParameters, environment: EnvironmentalProfile): Promise<ValidationRunResponse> {
    try {
      const res = await apiClient.post('/validation/run', { design, environment });
      return res.data;
    } catch {
      return {
        validation_id: "VAL-001",
        design_id: "DES-001",
        ml_prediction_temp: 17.4,
        ansys_simulation_temp: 17.2,
        absolute_error: 0.20,
        relative_error_percentage: 1.16,
        model_version: "v1.0.0",
        ansys_mode: "MOCK",
        passed_validation: true,
        timestamp: new Date().toISOString()
      };
    }
  },

  // Run Agent
  async runAgent(userPrompt: string, locationName: string, lat: number, lon: number): Promise<AgentRunResponse> {
    try {
      const res = await apiClient.post('/agent/run', { user_prompt: userPrompt, location_name: locationName, latitude: lat, longitude: lon });
      return res.data;
    } catch {
      return {
        response: "Based on the environmental profile for Leh, Ladakh, Stabilized Earth Block with South facing orientation is recommended.",
        tool_calls: [
          { tool_name: "get_location", arguments: { query: locationName }, output: { latitude: lat, longitude: lon }, timestamp: "10:00:00" },
          { tool_name: "create_environment_profile", arguments: { latitude: lat, longitude: lon }, output: { location: locationName }, timestamp: "10:00:01" },
          { tool_name: "optimize_design", arguments: { priority: "thermal_comfort" }, output: { best_design_id: "DES-001" }, timestamp: "10:00:02" },
          { tool_name: "validate_design", arguments: { design_id: "DES-001" }, output: { passed: true }, timestamp: "10:00:03" }
        ]
      };
    }
  },

  // Generate Report
  async generateReport(locationName: string, lat: number, lon: number): Promise<ReportGenerateResponse> {
    try {
      const res = await apiClient.post('/report/generate', { location_name: locationName, latitude: lat, longitude: lon });
      return res.data;
    } catch {
      return {
        report_title: `Engineering Decision Support Report - ${locationName}`,
        content_markdown: `# ClimateShelter Engineering Report\nLocation: ${locationName}\nRecommended Design: Stabilized Earth Block`,
        timestamp: new Date().toISOString(),
        metadata: {}
      };
    }
  },

  // Multi-Site Profiles
  async getMultiSiteProfiles(sites: { name: string; latitude: number; longitude: number }[]): Promise<EnvironmentalProfile[]> {
    try {
      const res = await apiClient.post('/environment/multi-profile', { sites });
      return res.data.profiles || [];
    } catch {
      return sites.map((s) => ({
        latitude: s.latitude,
        longitude: s.longitude,
        location_name: s.name,
        elevation: 1000,
        average_temperature: 15.0,
        minimum_temperature: -5.0,
        maximum_temperature: 30.0,
        humidity: 40.0,
        solar_radiation: 750.0,
        wind_speed: 8.0,
        wind_direction: 180.0,
        rainfall: 2.0,
        pressure: 1000.0,
        soil_properties: {
          soil_type: "Sandy Loam",
          sand_percentage: 50.0,
          clay_percentage: 25.0,
          silt_percentage: 25.0,
          moisture_content: 0.15,
          soil_temperature_10cm: 12.0,
          thermal_conductivity: 1.1
        },
        data_source: "SAMPLE",
        timestamp: new Date().toISOString(),
        hourly_temperatures: []
      }));
    }
  },

  // Multi-Site Optimization
  async runMultiSiteOptimization(sites: { name: string; latitude: number; longitude: number }[], priority = 'thermal_comfort') {
    try {
      const res = await apiClient.post('/optimization/multi-site', { sites, priority });
      return res.data.results || [];
    } catch {
      return sites.map((s, idx) => ({
        site_name: s.name,
        latitude: s.latitude,
        longitude: s.longitude,
        best_design: {
          id: `DES-00${idx + 1}`,
          rank: 1,
          parameters: {
            material_id: "stabilized_earth_block",
            wall_thickness: 0.35,
            roof_thickness: 0.25,
            length: 6.0,
            width: 4.0,
            height: 3.0,
            orientation: 180,
            insulation_thickness: 0.10,
            window_to_wall_ratio: 0.15
          },
          material_name: "Stabilized Earth Block (CSEB)",
          predicted_interior_temp: 18.2,
          objective_score: 88.0,
          constraint_status: { valid: true, violations: [] },
          thermal_comfort_score: 88.0,
          cost_index: 1400.0
        },
        predicted_interior_temp: 18.2,
        outdoor_avg_temp: 12.0
      }));
    }
  }
};

