# ANSYS Integration Guide for ClimateShelter AI

## Overview
ClimateShelter AI uses **ANSYS Mechanical / APDL** as the high-fidelity engineering reference for thermal simulations. 

When ANSYS is not installed in the local runtime environment, the backend automatically operates via the `MockANSYSProvider` adapter, emitting clearly labeled synthetic test data to ensure software functionality without disguising mock results as real ANSYS outputs.

## Real ANSYS Configuration
To connect a live ANSYS installation:

1. Install PyMAPDL (`pip install ansys-mapdl-core`).
2. Update your `.env` file:
   ```env
   ANSYS_MODE=pymapdl
   ANSYS_EXECUTABLE_PATH=C:/Program Files/ANSYS Inc/v231/ansys/bin/winx64/ansys231.exe
   ```
3. Start the FastAPI backend server. The system will automatically detect the ANSYS executable and execute APDL macros directly in batch mode.
