'use client';
import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Activity,
  Box,
  BrainCircuit,
  CloudSun,
  Gauge,
  Layers3,
  MapPin,
  Rotate3D,
  ShieldCheck,
  SlidersHorizontal,
  Thermometer,
  Wind,
  Zap,
  ArrowRight,
  Cpu
} from 'lucide-react';
import {
  AreaChart,
  Area,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from 'recharts';
import { api } from '@/lib/api';
import { EnvironmentalProfile, OptimizationResponse } from '@/lib/types';

const temperatureData = [
  { time: '00:00', indoor: 12, outdoor: -18 },
  { time: '03:00', indoor: 10, outdoor: -20 },
  { time: '06:00', indoor: 9, outdoor: -21 },
  { time: '09:00', indoor: 13, outdoor: -17 },
  { time: '12:00', indoor: 17, outdoor: -12 },
  { time: '15:00', indoor: 18, outdoor: -10 },
  { time: '18:00', indoor: 17, outdoor: -14 },
  { time: '21:00', indoor: 14, outdoor: -19 },
  { time: '24:00', indoor: 12, outdoor: -18 },
];

export default function HomePage() {
  const [profile, setProfile] = useState<EnvironmentalProfile | null>(null);
  const [optimization, setOptimization] = useState<OptimizationResponse | null>(null);
  const [selectedPriority, setSelectedPriority] = useState('Maximum Thermal Comfort');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      const envData = await api.getEnvironmentProfile(34.1526, 77.5771, "Leh, Ladakh");
      setProfile(envData);
      const optData = await api.runOptimization(envData);
      setOptimization(optData);
      setLoading(false);
    }
    loadData();
  }, []);

  return (
    <div className="space-y-6">
      {/* PAGE HEADING */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#101c2c] border border-[#1b2f48] p-6 rounded-2xl">
        <div>
          <span className="text-[10px] font-mono text-[#A5BE00] font-bold tracking-widest uppercase block mb-1">
            CLIMATE-AWARE ENGINEERING PLATFORM
          </span>
          <h1 className="text-2xl md:text-3xl font-bold text-[#EBF2FA] tracking-tight m-0">
            Thermal Design Command Center
          </h1>
          <p className="text-sm text-gray-300 mt-1 max-w-2xl">
            Transform location and environmental data into optimized, climate-aware shelter designs using simulation, machine learning, and AI.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/design"
            className="flex items-center gap-2 bg-[#064789] hover:bg-[#427AA1] text-white font-medium text-xs px-4 py-2.5 rounded-xl shadow-lg border border-[#427AA1] transition-all"
          >
            <BrainCircuit size={16} />
            <span>Generate AI Design</span>
            <ArrowRight size={14} />
          </Link>
        </div>
      </div>


      {/* MAIN DASHBOARD GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* LEFT PANEL: INPUT PARAMETERS */}
        <div className="lg:col-span-3 bg-[#16171d] border border-[#2e303a] rounded-2xl p-5 space-y-5">
          <div className="border-b border-[#2e303a] pb-3">
            <h3 className="text-sm font-bold text-white m-0 uppercase font-mono">INPUT PARAMETERS</h3>
            <span className="text-[10px] font-mono text-gray-500">DESIGN CONFIGURATION</span>
          </div>

          <div className="space-y-2">
            <label className="text-[10px] font-mono text-gray-400 block uppercase">CURRENT LOCATION</label>
            <div className="flex items-center justify-between bg-[#121319] border border-[#2e303a] px-3 py-2 rounded-xl text-xs">
              <div className="flex items-center gap-2 text-white font-medium">
                <MapPin size={15} className="text-blue-400" />
                <span>Leh, Ladakh</span>
              </div>
              <span className="text-[9px] font-mono bg-emerald-950 text-emerald-400 border border-emerald-800 px-1.5 py-0.5 rounded">
                ACTIVE
              </span>
            </div>
          </div>

          <div className="space-y-3 pt-2">
            <label className="text-[10px] font-mono text-gray-400 block uppercase">ENVIRONMENTAL DATA</label>

            <ClimateRow icon={<Thermometer size={15} className="text-rose-400" />} label="Ambient Temp" value={profile ? `${profile.average_temperature}°C` : "-12°C"} percent={22} />
            <ClimateRow icon={<CloudSun size={15} className="text-amber-400" />} label="Humidity" value={profile ? `${profile.humidity}%` : "25%"} percent={25} />
            <ClimateRow icon={<Zap size={15} className="text-yellow-400" />} label="Solar Irradiance" value={profile ? `${profile.solar_radiation} W/m²` : "850 W/m²"} percent={78} />
            <ClimateRow icon={<Wind size={15} className="text-cyan-400" />} label="Wind Speed" value={profile ? `${profile.wind_speed} m/s` : "12 m/s"} percent={52} />
            <ClimateRow icon={<Gauge size={15} className="text-indigo-400" />} label="Pressure" value={profile ? `${profile.pressure} hPa` : "610 hPa"} percent={61} />
          </div>

          <div className="border-t border-[#2e303a] pt-4 space-y-2 font-mono text-xs">
            <label className="text-[10px] font-mono text-gray-400 block uppercase">SHELTER PARAMETERS</label>
            <ParamRow label="Length" value="6.0 m" />
            <ParamRow label="Width" value="4.0 m" />
            <ParamRow label="Height" value="3.0 m" />
            <ParamRow label="Material" value="Stabilized Earth Block" />
            <ParamRow label="Orientation" value="180° SOUTH" />
          </div>
        </div>

        {/* CENTER VIEWER: 3D PHYSICS MODEL */}
        <div className="lg:col-span-6 bg-[#16171d] border border-[#2e303a] rounded-2xl p-5 flex flex-col justify-between relative overflow-hidden">
          <div className="flex items-center justify-between border-b border-[#2e303a] pb-3 z-10">
            <div>
              <h3 className="text-sm font-bold text-white m-0 uppercase font-mono">THERMAL SIMULATION VIEWER</h3>
              <span className="text-[10px] font-mono text-gray-500">3D PHYSICS MODEL</span>
            </div>

            <div className="flex items-center gap-2">
              <button className="flex items-center gap-1 text-[11px] font-mono bg-[#121319] hover:bg-[#222530] text-gray-300 px-2.5 py-1 rounded-lg border border-[#2e303a]">
                <Rotate3D size={13} /> Rotate
              </button>
              <button className="flex items-center gap-1 text-[11px] font-mono bg-[#121319] hover:bg-[#222530] text-gray-300 px-2.5 py-1 rounded-lg border border-[#2e303a]">
                <Box size={13} /> Cutaway
              </button>
            </div>
          </div>

          {/* INTERACTIVE 3D SIMULATION CANVAS */}
          <div className="my-6 h-72 rounded-xl bg-[#0d0e13] border border-[#262833] relative flex items-center justify-center viewer-grid overflow-hidden">
            <div className="absolute top-3 left-3 flex items-center gap-2 text-[10px] font-mono bg-blue-950/80 border border-blue-600/40 text-blue-300 px-2.5 py-1 rounded-md">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-ping"></span>
              ANSYS THERMAL VALIDATION: <strong>CONNECTED</strong>
            </div>

            {/* SOLAR RAYS VISUALIZATION */}
            <div className="absolute top-4 right-12 w-20 h-20 rounded-full bg-amber-500/10 border border-amber-500/30 flex items-center justify-center solar-glow">
              <Zap size={24} className="text-amber-400 animate-pulse" />
            </div>

            {/* SHELTER 3D STRUCTURAL GRAPHIC */}
            <div className="w-56 h-40 bg-[#161922] border-2 border-blue-500/50 rounded-lg relative flex flex-col justify-between p-3 shadow-2xl">
              {/* Roof */}
              <div className="w-full h-4 bg-gradient-to-r from-amber-600/40 via-blue-500/40 to-cyan-500/40 rounded border border-blue-400/40 text-[9px] font-mono text-center text-blue-200 flex items-center justify-center">
                REFLECTIVE ROOF DAMPING
              </div>

              {/* Thermal Core */}
              <div className="my-auto text-center space-y-1">
                <span className="text-[10px] font-mono text-gray-400 block">THERMAL MASS CORE</span>
                <div className="text-lg font-bold font-mono text-white tracking-wider">
                  {optimization ? `${optimization.best_design.predicted_interior_temp}°C` : "17.4°C"}
                </div>
                <span className="text-[9px] font-mono text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-800/40">
                  COMFORT RANGE
                </span>
              </div>

              {/* Windows & Doors */}
              <div className="flex justify-between items-end">
                <div className="w-8 h-8 bg-cyan-900/40 border border-cyan-400/40 rounded flex items-center justify-center text-[8px] font-mono text-cyan-300">
                  WWR 15%
                </div>
                <div className="w-6 h-10 bg-amber-900/40 border border-amber-500/40 rounded"></div>
              </div>
            </div>

            {/* TEMPERATURE GRADIENT LEGEND */}
            <div className="absolute bottom-3 right-3 bg-[#121319]/90 border border-[#2e303a] p-2 rounded-lg text-[9px] font-mono space-y-1">
              <span className="text-gray-400 block">TEMPERATURE</span>
              <div className="w-32 h-2 rounded bg-gradient-to-r from-blue-600 via-emerald-500 to-rose-600"></div>
              <div className="flex justify-between text-gray-400">
                <span>-20°C</span>
                <span>18°C</span>
                <span>38°C</span>
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between text-xs font-mono text-gray-400 border-t border-[#2e303a] pt-3">
            <span className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              SIMULATION LIVE: ML SURROGATE RUNNING
            </span>
            <span className="text-blue-400">PASSED BOUNDARY CHECK</span>
          </div>
        </div>

        {/* RIGHT PANEL: ANALYSIS & RECOMMENDATIONS */}
        <div className="lg:col-span-3 bg-[#16171d] border border-[#2e303a] rounded-2xl p-5 space-y-5">
          <div className="border-b border-[#2e303a] pb-3">
            <h3 className="text-sm font-bold text-white m-0 uppercase font-mono">ANALYSIS & AI RECOMMENDATIONS</h3>
            <span className="text-[10px] font-mono text-gray-500">AI DECISION SUPPORT</span>
          </div>

          <div className="space-y-2">
            <label className="text-[10px] font-mono text-gray-400 block uppercase">DESIGN PRIORITY</label>
            <div className="space-y-1.5">
              {['Maximum Thermal Comfort', 'Balanced Performance', 'Maximum Sustainability', 'Minimum Cost'].map((p) => (
                <button
                  key={p}
                  onClick={() => setSelectedPriority(p)}
                  className={`w-full text-left px-3 py-2 rounded-xl text-xs font-medium transition-all flex items-center justify-between ${
                    selectedPriority === p
                      ? 'bg-blue-600/20 text-blue-400 border border-blue-500/40'
                      : 'bg-[#121319] text-gray-400 hover:text-white border border-[#2e303a]'
                  }`}
                >
                  <span>{p}</span>
                  <span className={`w-2 h-2 rounded-full ${selectedPriority === p ? 'bg-blue-400' : 'bg-transparent'}`}></span>
                </button>
              ))}
            </div>
          </div>

          <div className="bg-[#121319] border border-[#2e303a] rounded-xl p-4 space-y-3">
            <div className="flex justify-between items-start">
              <div>
                <span className="text-[9px] font-mono text-gray-500 block uppercase">RECOMMENDED MATERIAL</span>
                <h4 className="text-sm font-bold text-white m-0">
                  {optimization ? optimization.best_design.material_name : "Stabilized Earth Block"}
                </h4>
              </div>
              <div className="w-9 h-9 rounded-lg bg-blue-600/20 border border-blue-500/40 text-blue-400 font-mono font-bold text-sm flex items-center justify-center">
                {optimization ? optimization.best_design.objective_score.toFixed(0) : "89"}
              </div>
            </div>

            <p className="text-xs text-gray-400 leading-relaxed">
              Recommended for high-altitude cold conditions due to high thermal mass and local soil compatibility.
            </p>

            <div className="space-y-2 font-mono text-xs pt-1">
              <div className="flex justify-between text-[11px] text-gray-400">
                <span>THERMAL SCORE</span>
                <strong className="text-white">89 / 100</strong>
              </div>
              <div className="w-full bg-[#1e202a] h-1.5 rounded-full overflow-hidden">
                <div className="bg-blue-500 h-full w-[89%]"></div>
              </div>
            </div>
          </div>

          <div className="bg-blue-950/30 border border-blue-800/30 rounded-xl p-4 flex gap-3 items-start">
            <BrainCircuit size={18} className="text-blue-400 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <span className="text-[10px] font-mono text-blue-400 block uppercase">AI INSIGHT</span>
              <p className="text-xs text-gray-300 leading-relaxed">
                High solar irradiance ({profile ? profile.solar_radiation : "850"} W/m²) can be harvested during daytime. Increasing wall thermal mass reduces nighttime heating load.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* KPI METRICS GRID */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
        <MetricCard icon={<Thermometer className="text-rose-400" />} label="INDOOR TEMP" value={optimization ? `${optimization.best_design.predicted_interior_temp}°C` : "17.4°C"} sub="COMFORT RANGE" trend="+3.2°C" />
        <MetricCard icon={<Zap className="text-amber-400" />} label="SOLAR GAIN" value="18.6 kWh" sub="DAILY TOTAL" trend="+12%" />
        <MetricCard icon={<Wind className="text-cyan-400" />} label="HEAT LOSS" value="4.2 kW" sub="PASSIVE LOSS" trend="-18%" />
        <MetricCard icon={<Activity className="text-emerald-400" />} label="THERMAL AUTONOMY" value="9.6 hrs" sub="WITHOUT HEATER" trend="+1.8 hrs" />
        <MetricCard icon={<ShieldCheck className="text-indigo-400" />} label="MODEL R² SCORE" value="0.968" sub="MAE: 0.38°C" trend="HIGH ACCURACY" />
      </div>

      {/* BOTTOM SECTION: 24-HOUR THERMAL CHART & WORKFLOW */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-8 bg-[#16171d] border border-[#2e303a] rounded-2xl p-5 space-y-4">
          <div className="flex justify-between items-center border-b border-[#2e303a] pb-3">
            <div>
              <h3 className="text-sm font-bold text-white m-0 uppercase font-mono">THERMAL PERFORMANCE PREDICTION</h3>
              <span className="text-[10px] font-mono text-gray-500">24-HOUR INDOOR VS OUTDOOR CURVE</span>
            </div>

            <div className="flex items-center gap-4 text-xs font-mono">
              <span className="flex items-center gap-1.5 text-blue-400">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-500"></span> Indoor Temp
              </span>
              <span className="flex items-center gap-1.5 text-gray-500">
                <span className="w-2.5 h-2.5 rounded-full bg-gray-600"></span> Outdoor Temp
              </span>
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={temperatureData}>
                <defs>
                  <linearGradient id="indoorGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.4} />
                    <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" stroke="#4b5563" fontSize={11} axisLine={false} tickLine={false} />
                <YAxis stroke="#4b5563" fontSize={11} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#121319', borderColor: '#2e303a', borderRadius: '8px', fontSize: '12px' }} />
                <Area type="monotone" dataKey="indoor" stroke="#3b82f6" strokeWidth={2.5} fill="url(#indoorGrad)" />
                <Area type="monotone" dataKey="outdoor" stroke="#6b7280" strokeWidth={1.5} strokeDasharray="4 4" fill="none" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="lg:col-span-4 bg-[#16171d] border border-[#2e303a] rounded-2xl p-5 flex flex-col justify-between space-y-4">
          <div className="border-b border-[#2e303a] pb-3">
            <h3 className="text-sm font-bold text-white m-0 uppercase font-mono">DESIGN WORKFLOW</h3>
            <span className="text-[10px] font-mono text-gray-500">STEP 04 / 05 COMPLETE</span>
          </div>

          <div className="space-y-3 font-mono text-xs">
            <WorkflowItem step="01" title="CLIMATE ANALYSIS" done />
            <WorkflowItem step="02" title="SHELTER PARAMETERIZATION" done />
            <WorkflowItem step="03" title="ML SURROGATE PREDICTION" done />
            <WorkflowItem step="04" title="MULTI-OBJECTIVE OPTIMIZATION" active />
            <WorkflowItem step="05" title="ANSYS VALIDATION & EXPLANATION" />
          </div>

          <Link
            href="/results"
            className="w-full py-2.5 bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 border border-blue-500/40 font-mono text-xs rounded-xl flex items-center justify-center gap-2 transition-all"
          >
            <span>View Full Optimization Results</span>
            <ArrowRight size={14} />
          </Link>
        </div>
      </div>
    </div>
  );
}

function ClimateRow({ icon, label, value, percent }: { icon: React.ReactNode; label: string; value: string; percent: number }) {
  return (
    <div className="flex items-center justify-between text-xs bg-[#121319] p-2.5 rounded-xl border border-[#2e303a]">
      <div className="flex items-center gap-2.5">
        {icon}
        <div>
          <span className="text-gray-400 text-[11px] block leading-none">{label}</span>
          <strong className="text-white font-mono text-xs">{value}</strong>
        </div>
      </div>
      <div className="w-16 bg-[#1e202a] h-1.5 rounded-full overflow-hidden">
        <div className="bg-blue-500 h-full" style={{ width: `${percent}%` }}></div>
      </div>
    </div>
  );
}

function ParamRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between text-gray-400 text-[11px] py-1 border-b border-[#222530] last:border-none">
      <span>{label}</span>
      <strong className="text-white font-normal">{value}</strong>
    </div>
  );
}

function MetricCard({ icon, label, value, sub, trend }: { icon: React.ReactNode; label: string; value: string; sub: string; trend: string }) {
  return (
    <div className="bg-[#16171d] border border-[#2e303a] p-4 rounded-2xl space-y-2">
      <div className="flex justify-between items-center">
        <div className="w-8 h-8 rounded-lg bg-[#121319] border border-[#2e303a] flex items-center justify-center">
          {icon}
        </div>
        <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/60 px-1.5 py-0.5 rounded border border-emerald-800/40">
          {trend}
        </span>
      </div>
      <div>
        <span className="text-[10px] font-mono text-gray-500 block uppercase">{label}</span>
        <strong className="text-xl font-bold font-mono text-white block">{value}</strong>
        <span className="text-[10px] text-gray-400 block">{sub}</span>
      </div>
    </div>
  );
}

function WorkflowItem({ step, title, done, active }: { step: string; title: string; done?: boolean; active?: boolean }) {
  return (
    <div className={`p-2.5 rounded-xl border flex items-center gap-3 ${
      active
        ? 'bg-blue-600/15 border-blue-500/40 text-blue-400'
        : done
        ? 'bg-[#121319] border-[#2e303a] text-gray-300'
        : 'bg-[#121319]/40 border-[#2e303a]/40 text-gray-600'
    }`}>
      <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
        done ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' : active ? 'bg-blue-500 text-white' : 'bg-gray-800 text-gray-500'
      }`}>
        {done ? '✓' : step}
      </div>
      <span className="font-semibold text-[11px]">{title}</span>
    </div>
  );
}
