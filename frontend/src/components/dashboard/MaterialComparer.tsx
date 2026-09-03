'use client';
import React, { useState, useEffect } from 'react';
import { Layers3, CheckCircle2, Award, Zap, DollarSign, ShieldCheck, Flame } from 'lucide-react';
import { api } from '@/lib/api';
import { MaterialComparisonItem, MaterialComparisonResponse } from '@/lib/types';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

interface MaterialComparerProps {
  latitude?: number;
  longitude?: number;
  locationName?: string;
}

export const MaterialComparer: React.FC<MaterialComparerProps> = ({
  latitude = 34.1526,
  longitude = 77.5771,
  locationName = "Leh, Ladakh",
}) => {
  const [data, setData] = useState<MaterialComparisonResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchComparison() {
      setLoading(true);
      const res = await api.compareAllMaterials(latitude, longitude, locationName);
      setData(res);
      setLoading(false);
    }
    fetchComparison();
  }, [latitude, longitude, locationName]);

  if (loading || !data) {
    return <div className="p-6 font-mono text-xs text-gray-400">Comparing all material physical properties & ML predictions...</div>;
  }

  const chartData = data.materials.map((m) => ({
    name: m.material_name.split(' ')[0],
    PredictedTemp: m.predicted_interior_temp,
    ComfortScore: m.thermal_comfort_score,
  }));

  const bestMat = data.materials[0];

  return (
    <div className="bg-[#16171d] border border-[#2e303a] p-6 rounded-2xl space-y-6 font-sans">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#2e303a] pb-4">
        <div>
          <span className="text-[10px] font-mono text-amber-400 font-bold tracking-widest uppercase block mb-1">
            MATERIAL PHYSICAL PROPERTY & THERMAL COMPARISON
          </span>
          <h2 className="text-xl font-bold text-white tracking-tight m-0 flex items-center gap-2">
            <Layers3 size={20} className="text-amber-400" />
            <span>Comprehensive Material Comparison Matrix</span>
          </h2>
          <p className="text-xs text-gray-400 mt-1">
            Side-by-side evaluation of thermal conductivity ($k$), density, volumetric heat capacity, cost, and ML predicted thermal performance for <strong>{data.location_name}</strong>.
          </p>
        </div>

        <div className="bg-amber-950/40 border border-amber-500/40 px-3 py-1.5 rounded-xl font-mono text-xs text-amber-400 flex items-center gap-2">
          <Award size={16} />
          <span>TOP MATERIAL: {bestMat ? bestMat.material_name : "CSEB"}</span>
        </div>
      </div>

      {/* COMPARISON CHART */}
      <div className="bg-[#121319] border border-[#2e303a] p-5 rounded-xl space-y-3 font-mono">
        <div className="flex justify-between items-center">
          <h3 className="text-xs font-bold text-white uppercase m-0">Predicted Indoor Temp vs Thermal Score by Material</h3>
          <span className="text-[10px] text-gray-400">OUTDOOR AVG: {data.outdoor_avg_temp}°C</span>
        </div>

        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <XAxis dataKey="name" stroke="#4b5563" fontSize={10} axisLine={false} tickLine={false} />
              <YAxis stroke="#4b5563" fontSize={10} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ backgroundColor: '#121319', borderColor: '#2e303a', borderRadius: '8px', fontSize: '12px' }} />
              <Bar dataKey="PredictedTemp" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Predicted Indoor Temp (°C)" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* COMPARISON TABLE */}
      <div className="overflow-x-auto font-mono text-xs">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-[#2e303a] text-[10px] text-gray-400 uppercase bg-[#121319]">
              <th className="p-3">Rank</th>
              <th className="p-3">Material Name</th>
              <th className="p-3">Conductivity (k)</th>
              <th className="p-3">Density (ρ)</th>
              <th className="p-3">Heat Capacity</th>
              <th className="p-3">Cost (₹/m³)</th>
              <th className="p-3">Predicted Temp</th>
              <th className="p-3">Comfort Score</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#222530]">
            {data.materials.map((m) => (
              <tr key={m.material_id} className="hover:bg-[#121319]/60 transition-colors">
                <td className="p-3 font-bold text-blue-400">#{m.suitability_rank}</td>
                <td className="p-3 font-semibold text-white">{m.material_name}</td>
                <td className="p-3 text-cyan-400">{m.thermal_conductivity} W/m·K</td>
                <td className="p-3 text-gray-300">{m.density} kg/m³</td>
                <td className="p-3 text-gray-300">{m.volumetric_heat_capacity} kJ/m³K</td>
                <td className="p-3 text-emerald-400">₹{m.cost_estimate.toLocaleString('en-IN')}</td>
                <td className="p-3 font-bold text-blue-400">{m.predicted_interior_temp}°C</td>

                <td className="p-3">
                  <span className="bg-blue-950 text-blue-400 border border-blue-800 px-2 py-0.5 rounded font-bold">
                    {m.thermal_comfort_score} / 100
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
