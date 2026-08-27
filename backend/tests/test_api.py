from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["service"] == "ClimateShelter AI Backend"

def test_location_search():
    response = client.post("/api/location", json={"query": "Leh"})
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) > 0

def test_environment_profile():
    payload = {"latitude": 34.1526, "longitude": 77.5771, "location_name": "Leh, Ladakh"}
    response = client.post("/api/environment/profile", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["location_name"] == "Leh, Ladakh"
    assert "soil_properties" in data

def test_materials_endpoint():
    response = client.get("/api/materials")
    assert response.status_code == 200
    materials = response.json()
    assert len(materials) >= 4

def test_ml_status_and_predict():
    status_resp = client.get("/api/ml/status")
    assert status_resp.status_code == 200
    
    predict_payload = {
        "design": {
            "material_id": "stabilized_earth_block",
            "wall_thickness": 0.35,
            "roof_thickness": 0.20,
            "length": 6.0,
            "width": 4.0,
            "height": 3.0,
            "orientation": 180.0,
            "insulation_thickness": 0.08,
            "window_to_wall_ratio": 0.15
        },
        "environment": {
            "latitude": 34.1526,
            "longitude": 77.5771,
            "location_name": "Leh, Ladakh",
            "elevation": 3500.0,
            "average_temperature": -12.0,
            "minimum_temperature": -21.0,
            "maximum_temperature": -5.0,
            "humidity": 25.0,
            "solar_radiation": 850.0,
            "wind_speed": 12.0,
            "wind_direction": 190.0,
            "rainfall": 1.2,
            "pressure": 610.0,
            "soil_properties": {
                "soil_type": "Gravelly Sandy Loam",
                "sand_percentage": 65.0,
                "clay_percentage": 15.0,
                "silt_percentage": 20.0,
                "moisture_content": 0.08,
                "soil_temperature_10cm": -4.2,
                "thermal_conductivity": 0.95
            },
            "data_source": "SAMPLE",
            "timestamp": "2026-08-27T00:00:00Z"
        }
    }
    pred_resp = client.post("/api/ml/predict", json=predict_payload)
    assert pred_resp.status_code == 200
    pred_data = pred_resp.json()
    assert "predicted_interior_temperature" in pred_data

def test_ansys_simulation_mock():
    payload = {
        "design": {
            "material_id": "stabilized_earth_block",
            "wall_thickness": 0.30,
            "roof_thickness": 0.20,
            "length": 6.0,
            "width": 4.0,
            "height": 3.0,
            "orientation": 180.0,
            "insulation_thickness": 0.08,
            "window_to_wall_ratio": 0.15
        },
        "environment": {
            "latitude": 34.1526,
            "longitude": 77.5771,
            "location_name": "Leh, Ladakh",
            "elevation": 3500.0,
            "average_temperature": -12.0,
            "minimum_temperature": -21.0,
            "maximum_temperature": -5.0,
            "humidity": 25.0,
            "solar_radiation": 850.0,
            "wind_speed": 12.0,
            "wind_direction": 190.0,
            "rainfall": 1.2,
            "pressure": 610.0,
            "soil_properties": {
                "soil_type": "Gravelly Sandy Loam",
                "sand_percentage": 65.0,
                "clay_percentage": 15.0,
                "silt_percentage": 20.0,
                "moisture_content": 0.08,
                "soil_temperature_10cm": -4.2,
                "thermal_conductivity": 0.95
            },
            "data_source": "SAMPLE",
            "timestamp": "2026-08-27T00:00:00Z"
        }
    }
    sim_resp = client.post("/api/simulation/run", json=payload)
    assert sim_resp.status_code == 200
    sim_data = sim_resp.json()
    assert sim_data["ansys_mode"] in ["MOCK", "REAL"]
    assert "apdl_script_preview" in sim_data
