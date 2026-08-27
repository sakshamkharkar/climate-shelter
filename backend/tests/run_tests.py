import unittest
import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi.testclient import TestClient
from backend.app.main import app

class TestClimateShelterAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_check(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "online")

    def test_location_search(self):
        res = self.client.post("/api/location", json={"query": "Leh"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(len(data["results"]) > 0)

    def test_environment_profile(self):
        payload = {"latitude": 34.1526, "longitude": 77.5771, "location_name": "Leh, Ladakh"}
        res = self.client.post("/api/environment/profile", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["location_name"], "Leh, Ladakh")

    def test_materials(self):
        res = self.client.get("/api/materials")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(res.json()) >= 4)

    def test_ml_predict(self):
        payload = {
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
        res = self.client.post("/api/ml/predict", json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertIn("predicted_interior_temperature", res.json())

    def test_agent_run(self):
        res = self.client.post("/api/agent/run", json={"location_name": "Leh, Ladakh", "latitude": 34.1526, "longitude": 77.5771})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(len(data["tool_calls"]) >= 4)

    def test_multi_site_endpoints(self):
        sites_payload = {
            "sites": [
                {"name": "Site A", "latitude": 34.1526, "longitude": 77.5771},
                {"name": "Site B", "latitude": 30.0444, "longitude": 31.2357}
            ]
        }
        res_prof = self.client.post("/api/environment/multi-profile", json=sites_payload)
        self.assertEqual(res_prof.status_code, 200)
        self.assertEqual(len(res_prof.json()["profiles"]), 2)

        res_opt = self.client.post("/api/optimization/multi-site", json=sites_payload)
        self.assertEqual(res_opt.status_code, 200)
        self.assertEqual(len(res_opt.json()["results"]), 2)

if __name__ == "__main__":
    unittest.main()

