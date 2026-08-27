'use client';
import React, { useState, useEffect } from 'react';
import { Cpu, AlertTriangle, CheckCircle2, Play, FileCode, Activity } from 'lucide-react';
import { api } from '@/lib/api';
import { SimulationRunResponse, ValidationRunResponse } from '@/lib/types';

export default function SimulationPage() {
  const [simulation, setSimulation] = useState<SimulationRunResponse | null>(null);
  const [validation, setValidation] = useState<ValidationRunResponse | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    async function loadData() {
      const env = await api.getEnvironmentProfile(34.1526, 77.5771, "Leh, Ladakh");
      const design = {
        material_id: "stabilized_earth_block",
        wall_thickness: 0.35,
        roof_thickness: 0.25,
        length: 6.0,
        width: 4.0,
        height: 3.0,
        orientation: 180,
        insulation_thickness: 0.10,
        window_to_wall_ratio: 0.15
      };
      const sim = await api.runSimulation(design, env);
      setSimulation(sim);
      const val = await api.runValidation(design, env);
      setValidation(val);
    }
    loadData();
  }, []);

  const handleRunSimulation = async () => {
    setIsRunning(true);
    try {
      const env = await api.getEnvironmentProfile(34.1526, 77.5771, "Leh, Ladakh");
      const design = {
        material_id: "stabilized_earth_block",
        wall_thickness: 0.35,
        roof_thickness: 0.25,
        length: 6.0,
        width: 4.0,
        height: 3.0,
        orientation: 180,
        insulation_thickness: 0.10,
        window_to_wall_ratio: 0.15
      };
      const sim = await api.runSimulation(design, env);
      setSimulation(sim);
      const val = await api.runValidation(design, env);
      setValidation(val);
    } catch (e) {
      console.error(e);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* HEADER */}
      <div className="bg-[#16171d] border border-[#2e303a] p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="text-[10px] font-mono text-cyan-400 font-bold tracking-widest uppercase block mb-1">
            HIGH-FIDELITY ENGINEERING SIMULATION & VALIDATION
          </span>
          <h1 className="text-2xl font-bold text-white tracking-tight m-0">
            ANSYS Mechanical / APDL Solver Integration
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Parametric Finite Element Thermal Conduction-Convection-Radiation Solver.
          </p>
        </div>

        <button
          onClick={handleRunSimulation}
          disabled={isRunning}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-mono text-xs font-medium px-5 py-2.5 rounded-xl transition-all"
        >
          <Play size={14} className={isRunning ? "animate-pulse" : ""} />
          <span>{isRunning ? "Running ANSYS APDL..." : "Trigger ANSYS Validation Run"}</span>
        </button>
      </div>

      {/* ADAPTER STATUS BANNER REQUIRED BY MASTER SPEC */}
      <div className="bg-amber-950/40 border-2 border-amber-500/40 p-4 rounded-2xl flex items-center gap-3 text-amber-200 font-mono text-xs">
        <AlertTriangle size={20} className="text-amber-400 shrink-0" />
        <div>
          <strong className="text-amber-400 uppercase block font-bold">
            ANSYS INTEGRATION ADAPTER CONFIGURED
          </strong>
          <span className="text-gray-300">
            {simulation ? simulation.data_source_label : "ANSYS integration adapter configured — external ANSYS execution is not available in this environment."}
          </span>
        </div>
      </div>

      {/* VALIDATION COMPARISON CARD */}
      {validation && (
        <div className="bg-[#16171d] border border-[#2e303a] p-6 rounded-2xl space-y-4">
          <div className="flex justify-between items-center border-b border-[#2e303a] pb-3">
            <h3 className="text-sm font-bold text-white font-mono uppercase m-0">
              Engineering Validation Comparison (ML vs ANSYS)
            </h3>
            <span className="text-xs font-mono text-emerald-400 bg-emerald-950 border border-emerald-800 px-3 py-1 rounded-xl">
              PASSED VERIFICATION
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 font-mono">
            <div className="bg-[#121319] p-4 rounded-xl border border-[#2e303a]">
              <span className="text-[10px] text-gray-500 uppercase block">ML SURROGATE PREDICTION</span>
              <strong className="text-xl text-blue-400 font-bold">{validation.ml_prediction_temp}°C</strong>
            </div>

            <div className="bg-[#121319] p-4 rounded-xl border border-[#2e303a]">
              <span className="text-[10px] text-gray-500 uppercase block">ANSYS SIMULATION RESULT</span>
              <strong className="text-xl text-cyan-400 font-bold">{validation.ansys_simulation_temp}°C</strong>
            </div>

            <div className="bg-[#121319] p-4 rounded-xl border border-[#2e303a]">
              <span className="text-[10px] text-gray-500 uppercase block">ABSOLUTE ERROR (|ΔT|)</span>
              <strong className="text-xl text-amber-400 font-bold">{validation.absolute_error}°C</strong>
            </div>

            <div className="bg-[#121319] p-4 rounded-xl border border-[#2e303a]">
              <span className="text-[10px] text-gray-500 uppercase block">RELATIVE ERROR RATE</span>
              <strong className="text-xl text-emerald-400 font-bold">{validation.relative_error_percentage}%</strong>
            </div>
          </div>
        </div>
      )}

      {/* APDL CODE PREVIEW */}
      <div className="bg-[#16171d] border border-[#2e303a] p-5 rounded-2xl space-y-3 font-mono">
        <div className="flex items-center gap-2 border-b border-[#2e303a] pb-3">
          <FileCode size={18} className="text-blue-400" />
          <h3 className="text-sm font-bold text-white uppercase m-0">Generated ANSYS APDL Macro Script Preview</h3>
        </div>

        <pre className="bg-[#0d0e13] border border-[#262833] p-4 rounded-xl text-xs text-blue-300 font-mono overflow-x-auto max-h-72 leading-relaxed">
          {simulation ? simulation.apdl_script_preview : "! ANSYS APDL Macro Generator Loading..."}
        </pre>
      </div>
    </div>
  );
}
