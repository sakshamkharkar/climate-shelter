# Machine Learning Surrogate Pipeline

## Framework
The surrogate pipeline compares multiple regression algorithms:
- **Random Forest Regressor** (Best Model: $R^2 = 0.968$, $\text{MAE} = 0.38^\circ\text{C}$)
- **Gradient Boosting Regressor**
- **Linear Regression**

## Training Dataset
- **Size**: 1,200 physics-grounded simulation samples
- **Split**: 70% Train (840), 15% Validation (180), 15% Test (180)
- **Target**: `interior_temperature`

## Out-of-Domain Detection
The `check_input_domain` service checks input parameter boundaries (wall thickness, orientation, ambient temperature) against training distribution thresholds, issuing explicit domain warnings when inputs extend beyond validated ranges.
