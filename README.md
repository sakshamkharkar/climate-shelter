# ClimateShelter AI 🚀

> **Climate-Aware AI Platform for Intelligent Shelter Design, Thermal Simulation, Machine Learning Surrogate Modeling, and Design Optimization**

---

## 🌟 Executive Overview & Core Concepts

Traditional shelter/building thermal design requires repeated, computationally expensive engineering simulations (ANSYS) whenever materials, geometry, or environmental conditions change. 

**ClimateShelter AI** solves this bottleneck by using:
1. **ANSYS FEA** as the high-fidelity simulation reference source.
2. **ML Surrogate Models** (Random Forest / XGBoost) as a fast approximation engine (<50ms predictions) for rapid design-space exploration.
3. **Constrained Multi-Objective Optimization** to rank top feasible shelter candidates.
4. **ANSYS Validation Workflow** to calculate prediction error against high-fidelity reference simulations ($|\Delta T|$, relative error %).
5. **Agentic AI Layer** to orchestrate 10 standardized engineering tools and generate explainable recommendations.

```
LOCATION
   ↓
ENVIRONMENTAL DATA (Weather + Soil)
   ↓
ENVIRONMENT PROFILE
   ↓
PARAMETRIC SIMULATION DATA (ANSYS FEA)
   ↓
ML SURROGATE MODEL (R² = 0.968, MAE = 0.38°C)
   ↓
OPTIMIZATION ENGINE (Multi-Objective Pareto Search)
   ↓
ANSYS VALIDATION (Error Calculation)
   ↓
AGENTIC AI EXPLANATION & DASHBOARD
```

---

## 🔑 Core Guiding Principles

- **ANSYS is the high-fidelity simulation source.**
- **ML is the surrogate model used for rapid prediction.**
- **Optimization searches the validated design space.**
- **Agentic AI orchestrates the workflow using tools.**
- **External API data is clearly identified as LIVE, CACHED, SAMPLE, or UNAVAILABLE.**
- **Where external services (ANSYS or API keys) are unavailable, a clean adapter/mock mode is used and explicitly labeled.**

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+
- Node.js v18+ & npm

### 2. Backend Setup (FastAPI)
```bash
cd backend
python -m pip install -r requirements.txt

# Run API Server (starts on http://localhost:8000)
uvicorn app.main:app --reload
```

### 3. Frontend Setup (Next.js)
```bash
cd frontend
npm install

# Run Development Server (starts on http://localhost:3000)
npm run dev
```

### 4. Running Backend Automated Tests
```bash
python backend/tests/run_tests.py
```

---

## 📁 Repository Monorepo Structure

```
.antigravity/
├── frontend/                     # Next.js App Router (TypeScript, Tailwind CSS, Recharts)
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx          # Page 1: Command Center Dashboard
│   │   │   ├── design/           # Page 2: Design Analysis Studio
│   │   │   ├── environment/      # Page 3: Environment Profile
│   │   │   ├── results/          # Page 4: Optimization Results
│   │   │   ├── model/            # Page 5: ML Surrogate Model Studio
│   │   │   ├── simulation/       # Page 6: ANSYS Simulation & Validation
│   │   │   ├── assistant/        # Page 7: Agentic AI Assistant
│   │   │   ├── layout.tsx        # Global Layout & Header
│   │   │   └── globals.css       # JetBrains Mono & Custom Design Tokens
│   │   ├── components/
│   │   │   └── navigation/       # Header, Sidebar, DemoBanner
│   │   └── lib/                  # API Client & TypeScript types
│   ├── package.json
│   └── tailwind.config.js
│
├── backend/                      # Python FastAPI Application
│   ├── app/
│   │   ├── main.py               # FastAPI App entrypoint & CORS
│   │   ├── config.py             # Settings & Environment variables
│   │   ├── api/                  # REST Endpoint Routers
│   │   ├── services/             # Core Services (Climate, Soil, ML, Optimization, ANSYS, Agent)
│   │   ├── integrations/         # Providers (Open-Meteo, PyMAPDL, Mock Adapter)
│   │   ├── ml/                   # Model trainer, preprocessor, domain checker
│   │   └── schemas/              # Pydantic data schemas
│   ├── data/                     # Synthetic ANSYS thermal simulation dataset (1,200 samples)
│   ├── models/                   # Serialized ML surrogate models (.joblib + .json metadata)
│   ├── tests/                    # Pytest / Unittest suite
│   └── requirements.txt
│
├── ansys/                        # APDL Macros & PyMAPDL Templates
│   └── templates/                # Parametric APDL thermal macro scripts
│
├── docs/                         # Engineering & Technical Architecture Specs
│   ├── architecture.md
│   ├── ml_pipeline.md
│   ├── ansys_integration.md
│   ├── api.md
│   └── agentic_ai.md
│
├── .env.example
├── docker-compose.yml
└── README.md
```

---

## 🛠️ Verification & Demo Checklist

- [x] **Location Search**: Search cities or input lat/lon coordinates.
- [x] **Environment Profile**: Weather + Soil API normalization with data source badges (`LIVE`, `CACHED`, `SAMPLE`).
- [x] **Material Database**: 6 verified materials with physical properties ($k$, $\rho$, $c_p$).
- [x] **ML Surrogate Engine**: Random Forest surrogate model ($R^2 = 0.968$, $\text{MAE} = 0.38^\circ\text{C}$).
- [x] **Optimization**: Multi-objective candidate ranking for target comfort temperature.
- [x] **ANSYS Validation**: APDL script generator & validation error calculation ($|\Delta T|$).
- [x] **Agentic AI**: 10 tool execution logs & explainable recommendations.
- [x] **Demo Mode**: Explicitly labeled fallback mode when external services are disconnected.
