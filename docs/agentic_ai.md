# Agentic AI Architecture & Tool Calling Framework

## Overview
The Agentic AI layer orchestrates the decision workflow by executing standardized engineering tools. The LLM summarizes verified tool outputs rather than inventing engineering numbers.

## 10 Standardized Tools
1. `get_location`: Geocoding & coordinate resolution
2. `get_climate_data`: Meteorological weather data
3. `get_soil_data`: Geological soil parameters
4. `create_environment_profile`: Environmental profile normalization
5. `get_materials`: Material physical property database
6. `generate_design_candidates`: Design space candidate generator
7. `predict_thermal_performance`: ML surrogate thermal prediction
8. `optimize_design`: Multi-objective Pareto optimizer
9. `validate_design`: ANSYS validation error checker
10. `generate_report`: Executive markdown report renderer
