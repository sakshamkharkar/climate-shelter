import pandas as pd
import numpy as np
import os
import random

def generate_ansys_dataset(output_path: str, num_samples: int = 1200):
    np.random.seed(42)
    random.seed(42)

    materials = [
        {"id": "stabilized_earth_block", "k": 0.85, "density": 1800.0, "c_p": 880.0},
        {"id": "autoclaved_aerated_concrete", "k": 0.16, "density": 550.0, "c_p": 1000.0},
        {"id": "burnt_clay_brick", "k": 0.77, "density": 1900.0, "c_p": 840.0},
        {"id": "eps_insulated_concrete", "k": 0.038, "density": 1250.0, "c_p": 1100.0},
        {"id": "timber_frame", "k": 0.13, "density": 500.0, "c_p": 1600.0},
        {"id": "polyurethane_sandwich", "k": 0.022, "density": 40.0, "c_p": 1400.0},
    ]

    records = []

    for _ in range(num_samples):
        mat = random.choice(materials)
        wall_thick = round(random.uniform(0.10, 0.60), 3)
        roof_thick = round(random.uniform(0.08, 0.40), 3)
        length = round(random.uniform(3.0, 12.0), 2)
        width = round(random.uniform(3.0, 10.0), 2)
        height = round(random.uniform(2.4, 4.5), 2)
        orientation = round(random.uniform(0.0, 360.0), 1)
        insulation_thick = round(random.uniform(0.0, 0.20), 3)
        wwr = round(random.uniform(0.05, 0.40), 2)

        # Environmental conditions
        outdoor_temp = round(random.uniform(-25.0, 45.0), 1)
        humidity = round(random.uniform(10.0, 90.0), 1)
        solar_rad = round(random.uniform(100.0, 1100.0), 1)
        wind_speed = round(random.uniform(1.0, 25.0), 1)
        pressure = round(random.uniform(600.0, 1020.0), 1)

        # Physics-based heat conduction calculation
        # Thermal resistance R = d/k
        k_val = mat["k"]
        r_wall = (wall_thick / k_val) + (insulation_thick / 0.035) + 0.13
        r_roof = (roof_thick / k_val) + (insulation_thick / 0.035) + 0.13

        # South facing solar gain multiplier (orientation 180° gets max solar gain)
        orient_rad = np.radians(orientation)
        solar_orient_factor = max(0.2, np.cos(orient_rad - np.radians(180.0)))
        solar_gain = (solar_rad * solar_orient_factor * (1.0 + wwr * 0.5)) / 1000.0  # kW/m²

        # Thermal mass damping
        thermal_mass = (wall_thick * mat["density"] * mat["c_p"]) / 1000.0

        if outdoor_temp < 5.0:  # Cold climate: internal heating retention & solar heat gain
            interior_temp = outdoor_temp + (25.0 * (r_wall / (r_wall + 1.2))) + (12.0 * solar_gain) + (thermal_mass * 0.003)
        elif outdoor_temp > 28.0:  # Hot climate: insulation damping
            interior_temp = outdoor_temp - (12.0 * (r_wall / (r_wall + 1.0))) + (8.0 * solar_gain) - (insulation_thick * 15.0)
        else:  # Temperate
            interior_temp = outdoor_temp + (5.0 * solar_gain) + 2.0

        # Add slight natural Gaussian noise for simulation variance
        noise = np.random.normal(0.0, 0.4)
        interior_temp = round(float(interior_temp + noise), 2)

        records.append({
            "material": mat["id"],
            "thermal_conductivity": mat["k"],
            "density": mat["density"],
            "specific_heat": mat["c_p"],
            "wall_thickness": wall_thick,
            "roof_thickness": roof_thick,
            "length": length,
            "width": width,
            "height": height,
            "orientation": orientation,
            "insulation_thickness": insulation_thick,
            "window_to_wall_ratio": wwr,
            "outdoor_temperature": outdoor_temp,
            "humidity": humidity,
            "solar_radiation": solar_rad,
            "wind_speed": wind_speed,
            "pressure": pressure,
            "interior_temperature": interior_temp
        })

    df = pd.DataFrame(records)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} simulation records at {output_path}")

if __name__ == "__main__":
    target_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "ansys_thermal_dataset.csv")
    generate_ansys_dataset(target_path)
