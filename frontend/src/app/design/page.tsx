'use client';
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { SlidersHorizontal, MapPin, Layers3, BrainCircuit, Box, Check, Sparkles, AlertCircle } from 'lucide-react';
import { api } from '@/lib/api';
import { Material, DesignParameters, EnvironmentalProfile } from '@/lib/types';

export default function DesignAnalysisPage() {
  const router = useRouter();
  const [materials, setMaterials] = useState<Material[]>([]);
  const [locationName, setLocationName] = useState('Leh, Ladakh');
  const [lat, setLat] = useState(34.1526);
  const [lon, setLon] = useState(77.5771);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [design, setDesign] = useState<DesignParameters>({
    material_id: 'stabilized_earth_block',
    wall_thickness: 0.35,
    roof_thickness: 0.25,
    length: 6.0,
    width: 4.0,
    height: 3.0,
    orientation: 180,
    insulation_thickness: 0.10,
    window_to_wall_ratio: 0.15,
  });

  const [priority, setPriority] = useState('thermal_comfort');

  useEffect(() => {
    api.getMaterials().then(setMaterials);
  }, []);

  const handleLocationNameChange = async (nameVal: string) => {
    setLocationName(nameVal);
    if (nameVal.trim().length >= 3) {
      try {
        const results = await api.searchLocation(nameVal);
        if (results && results.length > 0) {
          const topMatch = results[0];
          setLat(topMatch.latitude);
          setLon(topMatch.longitude);
        }
      } catch (err) {
        console.warn("Geocoding lookup failed:", err);
      }
    }
  };

  const handleRunAnalysis = async () => {
    setIsSubmitting(true);
    try {
      const env = await api.getEnvironmentProfile(lat, lon, locationName);
      await api.runOptimization(env, priority);
      router.push('/results');
    } catch (e) {
      console.error(e);
    } finally {
      setIsSubmitting(false);
    }
  };


  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* HEADER */}
      <div className="bg-[#16171d] border border-[#2e303a] p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="text-[10px] font-mono text-blue-400 font-bold tracking-widest uppercase block mb-1">
            PARAMETRIC SHELTER DESIGN & OPTIMIZATION
          </span>
          <h1 className="text-2xl font-bold text-white tracking-tight m-0">
            Interactive Design Analysis Studio
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Configure material physical properties, geometrical dimensions, insulation layers, and thermal priorities.
          </p>
        </div>

        <button
          onClick={handleRunAnalysis}
          disabled={isSubmitting}
          className="flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs px-6 py-3 rounded-xl shadow-lg shadow-blue-600/20 transition-all font-mono uppercase"
        >
          {isSubmitting ? (
            <span>Running ML Optimization...</span>
          ) : (
            <>
              <BrainCircuit size={16} />
              <span>Run Design Analysis</span>
            </>
          )}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* LEFT COLUMN: LOCATION & MATERIAL PICKER */}
        <div className="lg:col-span-6 space-y-6">
          {/* LOCATION INPUT */}
          <div className="bg-[#16171d] border border-[#2e303a] p-5 rounded-2xl space-y-4">
            <div className="flex items-center gap-2 border-b border-[#2e303a] pb-3">
              <MapPin size={18} className="text-blue-400" />
              <h3 className="text-sm font-bold text-white font-mono uppercase m-0">1. Target Location</h3>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="sm:col-span-3">
                <label className="text-[10px] font-mono text-gray-400 block mb-1">LOCATION NAME</label>
                <input
                  type="text"
                  value={locationName}
                  onChange={(e) => setLocationName(e.target.value)}
                  className="w-full bg-[#121319] border border-[#2e303a] rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500 font-mono"
                />
              </div>
              <div>
                <label className="text-[10px] font-mono text-gray-400 block mb-1">LATITUDE (°N)</label>
                <input
                  type="number"
                  step="0.0001"
                  value={lat}
                  onChange={(e) => setLat(parseFloat(e.target.value) || 0)}
                  className="w-full bg-[#121319] border border-[#2e303a] rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500 font-mono"
                />
              </div>
              <div>
                <label className="text-[10px] font-mono text-gray-400 block mb-1">LONGITUDE (°E)</label>
                <input
                  type="number"
                  step="0.0001"
                  value={lon}
                  onChange={(e) => setLon(parseFloat(e.target.value) || 0)}
                  className="w-full bg-[#121319] border border-[#2e303a] rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500 font-mono"
                />
              </div>
            </div>
          </div>

          {/* MATERIAL SELECTION */}
          <div className="bg-[#16171d] border border-[#2e303a] p-5 rounded-2xl space-y-4">
            <div className="flex items-center gap-2 border-b border-[#2e303a] pb-3">
              <Layers3 size={18} className="text-amber-400" />
              <h3 className="text-sm font-bold text-white font-mono uppercase m-0">2. Primary Wall Material Selection</h3>
            </div>

            <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
              {materials.map((mat) => {
                const isSelected = design.material_id === mat.id;
                return (
                  <div
                    key={mat.id}
                    onClick={() => setDesign({ ...design, material_id: mat.id })}
                    className={`p-3 rounded-xl border transition-all cursor-pointer ${
                      isSelected
                        ? 'bg-blue-600/15 border-blue-500 text-white'
                        : 'bg-[#121319] border-[#2e303a] text-gray-400 hover:border-gray-600'
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <span className="font-bold text-xs text-white font-mono">{mat.name}</span>
                      {isSelected && <Check size={16} className="text-blue-400" />}
                    </div>
                    <p className="text-[11px] text-gray-400 mt-1 leading-snug">{mat.description}</p>
                    <div className="flex gap-4 text-[10px] font-mono text-gray-400 mt-2 pt-2 border-t border-[#222530]">
                      <span>k: <strong className="text-blue-400">{mat.thermal_conductivity} W/m·K</strong></span>
                      <span>Density: <strong className="text-gray-200">{mat.density} kg/m³</strong></span>
                      <span>Cost: <strong className="text-emerald-400">₹{mat.cost_estimate.toLocaleString('en-IN')}/m³</strong></span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: GEOMETRY & OPTIMIZATION SETTINGS */}
        <div className="lg:col-span-6 space-y-6">
          {/* GEOMETRY & THERMAL PARAMETERS */}
          <div className="bg-[#16171d] border border-[#2e303a] p-5 rounded-2xl space-y-5">
            <div className="flex items-center gap-2 border-b border-[#2e303a] pb-3">
              <Box size={18} className="text-cyan-400" />
              <h3 className="text-sm font-bold text-white font-mono uppercase m-0">3. Shelter Geometry & Insulation</h3>
            </div>

            <div className="space-y-4">
              <SliderControl
                label="Wall Thickness (m)"
                min={0.10}
                max={0.80}
                step={0.05}
                value={design.wall_thickness}
                onChange={(val) => setDesign({ ...design, wall_thickness: val })}
              />

              <SliderControl
                label="Roof Thickness (m)"
                min={0.08}
                max={0.50}
                step={0.02}
                value={design.roof_thickness}
                onChange={(val) => setDesign({ ...design, roof_thickness: val })}
              />

              <SliderControl
                label="Insulation Thickness (m)"
                min={0.0}
                max={0.30}
                step={0.02}
                value={design.insulation_thickness}
                onChange={(val) => setDesign({ ...design, insulation_thickness: val })}
              />

              <div className="grid grid-cols-3 gap-3 pt-2">
                <div>
                  <label className="text-[10px] font-mono text-gray-400 block mb-1">LENGTH (m)</label>
                  <input
                    type="number"
                    step="0.5"
                    value={design.length}
                    onChange={(e) => setDesign({ ...design, length: parseFloat(e.target.value) || 6.0 })}
                    className="w-full bg-[#121319] border border-[#2e303a] rounded-xl px-3 py-2 text-xs text-white font-mono"
                  />
                </div>
                <div>
                  <label className="text-[10px] font-mono text-gray-400 block mb-1">WIDTH (m)</label>
                  <input
                    type="number"
                    step="0.5"
                    value={design.width}
                    onChange={(e) => setDesign({ ...design, width: parseFloat(e.target.value) || 4.0 })}
                    className="w-full bg-[#121319] border border-[#2e303a] rounded-xl px-3 py-2 text-xs text-white font-mono"
                  />
                </div>
                <div>
                  <label className="text-[10px] font-mono text-gray-400 block mb-1">HEIGHT (m)</label>
                  <input
                    type="number"
                    step="0.5"
                    value={design.height}
                    onChange={(e) => setDesign({ ...design, height: parseFloat(e.target.value) || 3.0 })}
                    className="w-full bg-[#121319] border border-[#2e303a] rounded-xl px-3 py-2 text-xs text-white font-mono"
                  />
                </div>
              </div>

              <SliderControl
                label="Building Orientation (0-360° Azimuth, 180° = South)"
                min={0}
                max={360}
                step={15}
                value={design.orientation}
                onChange={(val) => setDesign({ ...design, orientation: val })}
              />

              <SliderControl
                label="Window-to-Wall Ratio (WWR)"
                min={0.05}
                max={0.50}
                step={0.05}
                value={design.window_to_wall_ratio}
                onChange={(val) => setDesign({ ...design, window_to_wall_ratio: val })}
              />
            </div>
          </div>

          {/* OPTIMIZATION OBJECTIVE */}
          <div className="bg-[#16171d] border border-[#2e303a] p-5 rounded-2xl space-y-4">
            <div className="flex items-center gap-2 border-b border-[#2e303a] pb-3">
              <Sparkles size={18} className="text-emerald-400" />
              <h3 className="text-sm font-bold text-white font-mono uppercase m-0">4. Optimization Priority</h3>
            </div>

            <div className="grid grid-cols-2 gap-3 font-mono text-xs">
              {[
                { id: 'thermal_comfort', label: 'Max Thermal Comfort' },
                { id: 'cost', label: 'Min Construction Cost' },
                { id: 'sustainable', label: 'Max Passive Autonomy' },
                { id: 'balanced', label: 'Balanced Optimization' }
              ].map((p) => (
                <button
                  key={p.id}
                  onClick={() => setPriority(p.id)}
                  className={`p-3 rounded-xl border text-left font-medium transition-all ${
                    priority === p.id
                      ? 'bg-emerald-950/40 border-emerald-500/50 text-emerald-400'
                      : 'bg-[#121319] border-[#2e303a] text-gray-400 hover:text-white'
                  }`}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function SliderControl({ label, min, max, step, value, onChange }: { label: string; min: number; max: number; step: number; value: number; onChange: (val: number) => void }) {
  return (
    <div className="space-y-1.5 font-mono">
      <div className="flex justify-between text-xs">
        <span className="text-gray-400">{label}</span>
        <strong className="text-blue-400">{value}</strong>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full h-1.5 bg-[#121319] rounded-lg appearance-none cursor-pointer accent-blue-500"
      />
    </div>
  );
}
