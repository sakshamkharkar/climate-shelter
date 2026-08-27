'use client';
import React, { useState, useEffect } from 'react';
import { Box, Award, CheckCircle2, SlidersHorizontal, ArrowRight, Layers3, Zap, ShieldCheck } from 'lucide-react';
import { api } from '@/lib/api';
import { OptimizationResponse, DesignCandidate } from '@/lib/types';
import { MaterialComparer } from '@/components/dashboard/MaterialComparer';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';


export default function ResultsPage() {
  const [data, setData] = useState<OptimizationResponse | null>(null);

  useEffect(() => {
    async function loadResults() {
      const env = await api.getEnvironmentProfile(34.1526, 77.5771, "Leh, Ladakh");
      const res = await api.runOptimization(env, "thermal_comfort");
      setData(res);
    }
    loadResults();
  }, []);

  if (!data) {
    return <div className="p-8 font-mono text-xs text-gray-400">Evaluating candidate design space...</div>;
  }

  const allCandidates = [data.best_design, ...data.alternatives];

  const comparisonData = allCandidates.map((c, idx) => ({
    name: `Rank #${c.rank} (${c.material_name.split(' ')[0]})`,
    PredictedTemp: c.predicted_interior_temp,
    ThermalScore: c.thermal_comfort_score,
  }));

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* HEADER */}
      <div className="bg-[#16171d] border border-[#2e303a] p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="text-[10px] font-mono text-emerald-400 font-bold tracking-widest uppercase block mb-1">
            OPTIMIZATION RESULTS & RANKED CANDIDATES
          </span>
          <h1 className="text-2xl font-bold text-white tracking-tight m-0">
            Top Feasible Shelter Configurations
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Evaluated {data.total_evaluated} candidate designs in {data.execution_time_ms}ms | Objective: {data.optimization_objective}
          </p>
        </div>

        <div className="flex items-center gap-2 font-mono text-xs">
          <span className="bg-emerald-950/60 border border-emerald-500/40 text-emerald-400 px-3 py-1.5 rounded-xl font-bold flex items-center gap-2">
            <CheckCircle2 size={15} />
            {allCandidates.length} CANDIDATES RANKED
          </span>
        </div>
      </div>

      {/* RECOMMENDED DESIGN SPOTLIGHT */}
      <div className="bg-gradient-to-r from-blue-950/40 via-[#16171d] to-[#16171d] border-2 border-blue-500/40 p-6 rounded-2xl space-y-4">
        <div className="flex justify-between items-start">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/40 text-blue-400 flex items-center justify-center">
              <Award size={22} />
            </div>
            <div>
              <span className="text-[10px] font-mono text-blue-400 font-bold tracking-wider uppercase block">
                RANK #1 — OPTIMAL RECOMMENDATION
              </span>
              <h2 className="text-xl font-bold text-white m-0">{data.best_design.material_name}</h2>
            </div>
          </div>

          <div className="text-right font-mono">
            <span className="text-[10px] text-gray-400 block uppercase">OBJECTIVE SCORE</span>
            <strong className="text-2xl text-blue-400 font-bold">{data.best_design.objective_score} / 100</strong>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 font-mono text-xs pt-2">
          <div className="bg-[#121319] p-3 rounded-xl border border-[#2e303a]">
            <span className="text-gray-500 text-[10px] block">PREDICTED INDOOR TEMP</span>
            <strong className="text-white text-base">{data.best_design.predicted_interior_temp}°C</strong>
          </div>
          <div className="bg-[#121319] p-3 rounded-xl border border-[#2e303a]">
            <span className="text-gray-500 text-[10px] block">WALL THICKNESS</span>
            <strong className="text-white text-base">{data.best_design.parameters.wall_thickness} m</strong>
          </div>
          <div className="bg-[#121319] p-3 rounded-xl border border-[#2e303a]">
            <span className="text-gray-500 text-[10px] block">ROOF THICKNESS</span>
            <strong className="text-white text-base">{data.best_design.parameters.roof_thickness} m</strong>
          </div>
          <div className="bg-[#121319] p-3 rounded-xl border border-[#2e303a]">
            <span className="text-gray-500 text-[10px] block">INSULATION</span>
            <strong className="text-white text-base">{data.best_design.parameters.insulation_thickness} m</strong>
          </div>
        </div>
      </div>

      {/* COMPARISON CHART & TABLE */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-7 bg-[#16171d] border border-[#2e303a] p-5 rounded-2xl space-y-4">
          <div className="border-b border-[#2e303a] pb-3">
            <h3 className="text-sm font-bold text-white font-mono uppercase m-0">Predicted Thermal Performance Comparison</h3>
            <span className="text-[10px] font-mono text-gray-500">INDOOR TEMPERATURE VS THERMAL COMFORT SCORE</span>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={comparisonData}>
                <XAxis dataKey="name" stroke="#4b5563" fontSize={10} axisLine={false} tickLine={false} />
                <YAxis stroke="#4b5563" fontSize={10} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#121319', borderColor: '#2e303a', borderRadius: '8px', fontSize: '12px' }} />
                <Bar dataKey="PredictedTemp" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Predicted Temp (°C)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* FEASIBLE CANDIDATES TABLE */}
        <div className="lg:col-span-5 bg-[#16171d] border border-[#2e303a] p-5 rounded-2xl space-y-3 font-mono">
          <div className="border-b border-[#2e303a] pb-3">
            <h3 className="text-sm font-bold text-white uppercase m-0">Top Candidate Designs</h3>
            <span className="text-[10px] text-gray-500">CONSTRAINED DESIGN SPACE RANKING</span>
          </div>

          <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
            {allCandidates.map((c) => (
              <div key={c.id} className="p-3 rounded-xl bg-[#121319] border border-[#2e303a] space-y-1.5">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-bold text-blue-400">#{c.rank} — {c.material_name}</span>
                  <span className="text-[10px] text-emerald-400 bg-emerald-950 px-2 py-0.5 rounded border border-emerald-800">
                    PASSED
                  </span>
                </div>
                <div className="flex justify-between text-[11px] text-gray-400">
                  <span>Predicted Temp: <strong className="text-white">{c.predicted_interior_temp}°C</strong></span>
                  <span>Score: <strong className="text-white">{c.objective_score}</strong></span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* COMPREHENSIVE MATERIAL COMPARISON ENGINE */}
      <div className="pt-4">
        <MaterialComparer />
      </div>
    </div>
  );
}

