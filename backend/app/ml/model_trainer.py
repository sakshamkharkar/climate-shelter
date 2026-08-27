import pandas as pd
import numpy as np
import os
import json
import joblib
from datetime import datetime
from typing import Dict, Any, Tuple

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

FEATURE_COLUMNS = [
    "material",
    "thermal_conductivity",
    "density",
    "specific_heat",
    "wall_thickness",
    "roof_thickness",
    "length",
    "width",
    "height",
    "orientation",
    "insulation_thickness",
    "window_to_wall_ratio",
    "outdoor_temperature",
    "humidity",
    "solar_radiation",
    "wind_speed",
    "pressure"
]

TARGET_COLUMN = "interior_temperature"

CATEGORICAL_FEATURES = ["material"]
NUMERICAL_FEATURES = [f for f in FEATURE_COLUMNS if f not in CATEGORICAL_FEATURES]

class SurrogateModelTrainer:
    def __init__(self, data_path: str, model_dir: str):
        self.data_path = data_path
        self.model_dir = model_dir

    def train_and_evaluate(self) -> Dict[str, Any]:
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Dataset file not found at {self.data_path}")

        df = pd.read_csv(self.data_path)
        
        X = df[FEATURE_COLUMNS]
        y = df[TARGET_COLUMN]

        # Train / Validation / Test split (70% / 15% / 15%)
        X_train_val, X_test, y_train_val, y_test = train_test_split(X, y, test_size=0.15, random_state=42)
        X_train, X_val, y_train, y_val = train_test_split(X_train_val, y_train_val, test_size=0.176, random_state=42)

        preprocessor = ColumnTransformer(
            transformers=[
                ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
                ("num", "passthrough", NUMERICAL_FEATURES)
            ]
        )

        candidate_models = {
            "Random Forest Regressor": RandomForestRegressor(n_estimators=100, random_state=42),
            "Gradient Boosting Regressor": GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, random_state=42),
            "Linear Regression": LinearRegression()
        }

        best_model_name = ""
        best_r2 = -float("inf")
        best_pipeline = None
        best_metrics = {}
        model_results = {}

        for name, regressor in candidate_models.items():
            pipeline = Pipeline(steps=[
                ("preprocessor", preprocessor),
                ("regressor", regressor)
            ])

            pipeline.fit(X_train, y_train)

            # Evaluate on validation set
            y_val_pred = pipeline.predict(X_val)
            val_mae = float(mean_absolute_error(y_val, y_val_pred))
            val_rmse = float(np.sqrt(mean_squared_error(y_val, y_val_pred)))
            val_r2 = float(r2_score(y_val, y_val_pred))

            # Evaluate on test set
            y_test_pred = pipeline.predict(X_test)
            test_mae = float(mean_absolute_error(y_test, y_test_pred))
            test_rmse = float(np.sqrt(mean_squared_error(y_test, y_test_pred)))
            test_r2 = float(r2_score(y_test, y_test_pred))

            model_results[name] = {
                "val_mae": round(val_mae, 4),
                "val_rmse": round(val_rmse, 4),
                "val_r2": round(val_r2, 4),
                "test_mae": round(test_mae, 4),
                "test_rmse": round(test_rmse, 4),
                "test_r2": round(test_r2, 4)
            }

            if val_r2 > best_r2:
                best_r2 = val_r2
                best_model_name = name
                best_pipeline = pipeline
                best_metrics = {
                    "mae": round(test_mae, 4),
                    "rmse": round(test_rmse, 4),
                    "r2": round(test_r2, 4),
                    "model_name": name,
                    "dataset_size": len(df),
                    "training_samples": len(X_train),
                    "validation_samples": len(X_val),
                    "test_samples": len(X_test),
                    "feature_count": len(FEATURE_COLUMNS),
                    "features": FEATURE_COLUMNS,
                    "target": TARGET_COLUMN,
                    "training_date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                }

        # Save best model
        os.makedirs(self.model_dir, exist_ok=True)
        model_path = os.path.join(self.model_dir, "surrogate_model.joblib")
        meta_path = os.path.join(self.model_dir, "model_metadata.json")

        joblib.dump(best_pipeline, model_path)
        with open(meta_path, "w") as f:
            json.dump(best_metrics, f, indent=2)

        return {
            "status": "SUCCESS",
            "best_model": best_model_name,
            "metrics": best_metrics,
            "all_models": model_results
        }
