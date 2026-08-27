# ANSYS FEA Integration & Adapter Specification

## Principles
1. **ANSYS is the Engineering Authority**: The ML model is a surrogate for rapid candidate search; ANSYS provides the validation benchmark.
2. **Transparent Adapter Pattern**: Supports `REAL` mode (PyMAPDL APDL macro execution) and `MOCK` adapter mode (physics-based heat balance calculations).
3. **Validation Error Calculation**:
   $$\text{Absolute Error} = |T_{\text{ML}} - T_{\text{ANSYS}}|$$
   $$\text{Relative Error} = \frac{|T_{\text{ML}} - T_{\text{ANSYS}}|}{T_{\text{ANSYS}}} \times 100\%$$
