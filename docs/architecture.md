# ClimateShelter AI — System Architecture

```
                         USER
                           │
                           ▼
                    NEXT.JS FRONTEND
                           │
                           ▼
                    FASTAPI BACKEND
                           │
                           ▼
                    AGENTIC AI LAYER
                           │
             ┌─────────────┼──────────────┐
             │             │              │
             ▼             ▼              ▼
        CLIMATE API     SOIL API     DESIGN ENGINE
             │             │              │
             └─────────────┼──────────────┘
                           ▼
                 ENVIRONMENT PROFILE
                           │
                           ▼
                  PARAMETRIC ANSYS
                           │
                           ▼
                  SIMULATION DATASET
                           │
                           ▼
                   ML SURROGATE
                           │
                           ▼
                   OPTIMIZATION
                           │
                           ▼
                  TOP CANDIDATES
                           │
                           ▼
                   ANSYS VALIDATION
                           │
                           ▼
                 EXPLAINABLE RESULT
                           │
                           ▼
                    WEB DASHBOARD
```

## Core Problem & Solution
High-fidelity engineering simulations (ANSYS) are computationally expensive when evaluating large design spaces. ClimateShelter AI solves this bottleneck by using a machine-learning surrogate model for rapid design-space exploration (<50ms), while maintaining ANSYS as the high-fidelity engineering reference for final validation.
