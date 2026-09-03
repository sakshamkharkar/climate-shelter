export interface LocationSearchResult {
  name: string;
  latitude: number;
  longitude: number;
  country?: string;
  elevation?: number;
  timezone?: string;
}

export interface SiteCoordinate {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
}

export interface SiteOptimizationResult {
  site_name: string;
  latitude: number;
  longitude: number;
  best_design: DesignCandidate;
  predicted_interior_temp: number;
  outdoor_avg_temp: number;
}


export interface SoilProperties {
  soil_type: string;
  sand_percentage: number;
  clay_percentage: number;
  silt_percentage: number;
  moisture_content: number;
  soil_temperature_10cm: number;
  thermal_conductivity: number;
}

export interface EnvironmentalProfile {
  latitude: number;
  longitude: number;
  location_name: string;
  elevation: number;
  average_temperature: number;
  minimum_temperature: number;
  maximum_temperature: number;
  humidity: number;
  solar_radiation: number;
  wind_speed: number;
  wind_direction: number;
  rainfall: number;
  pressure: number;
  soil_properties: SoilProperties;
  data_source: string; // LIVE, CACHED, SAMPLE, UNAVAILABLE
  timestamp: string;
  hourly_temperatures: number[];
}

export interface Material {
  id: string;
  name: string;
  thermal_conductivity: number;
  density: number;
  specific_heat: number;
  cost_estimate: number;
  availability: string;
  source: string;
  description?: string;
}

export interface MaterialComparisonItem {
  material_id: string;
  material_name: string;
  thermal_conductivity: number;
  density: number;
  specific_heat: number;
  cost_estimate: number;
  availability: string;
  predicted_interior_temp: number;
  thermal_comfort_score: number;
  volumetric_heat_capacity: number;
  suitability_rank: number;
}

export interface MaterialComparisonResponse {
  location_name: string;
  outdoor_avg_temp: number;
  materials: MaterialComparisonItem[];
}


export interface DesignParameters {
  material_id: string;
  wall_thickness: number;
  roof_thickness: number;
  length: number;
  width: number;
  height: number;
  orientation: number;
  insulation_thickness: number;
  window_to_wall_ratio: number;
}

export interface ConstraintValidation {
  valid: boolean;
  violations: string[];
}

export interface DesignCandidate {
  id: string;
  rank: number;
  parameters: DesignParameters;
  material_name: string;
  predicted_interior_temp: number;
  objective_score: number;
  constraint_status: ConstraintValidation;
  thermal_comfort_score: number;
  cost_index: number;
}

export interface MLMetrics {
  mae: number;
  rmse: number;
  r2: number;
  model_name: string;
  dataset_size: number;
  training_samples: number;
  validation_samples: number;
  test_samples: number;
  feature_count: number;
  features: string[];
  target: string;
  training_date: string;
}

export interface MLStatusResponse {
  status: string;
  active_model: string;
  metrics: MLMetrics | null;
  available_models: string[];
}

export interface MLPredictResponse {
  predicted_interior_temperature: number;
  model_version: string;
  model_type: string;
  domain_warning: boolean;
  domain_warning_message?: string;
  confidence_interval?: {
    min_estimate: number;
    max_estimate: number;
  };
}

export interface OptimizationResponse {
  id: string;
  best_design: DesignCandidate;
  alternatives: DesignCandidate[];
  total_evaluated: number;
  execution_time_ms: number;
  optimization_objective: string;
  timestamp: string;
}

export interface SimulationRunResponse {
  simulation_id: string;
  ansys_mode: string;
  status: string;
  interior_temperature: number;
  max_surface_temp: number;
  min_surface_temp: number;
  total_heat_flux: number;
  execution_time_seconds: number;
  apdl_script_preview: string;
  data_source_label: string;
  timestamp: string;
}

export interface ValidationRunResponse {
  validation_id: string;
  design_id: string;
  ml_prediction_temp: number;
  ansys_simulation_temp: number;
  absolute_error: number;
  relative_error_percentage: number;
  model_version: string;
  ansys_mode: string;
  passed_validation: boolean;
  timestamp: string;
}

export interface ToolCallLog {
  tool_name: string;
  arguments: Record<string, any>;
  output: Record<string, any>;
  timestamp: string;
}

export interface AgentRunResponse {
  response: string;
  tool_calls: ToolCallLog[];
  recommended_design?: Record<string, any>;
  environmental_summary?: Record<string, any>;
  validation_summary?: Record<string, any>;
}

export interface ReportGenerateResponse {
  report_title: string;
  content_markdown: string;
  timestamp: string;
  metadata: Record<string, any>;
}
