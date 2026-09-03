'use client';
import React, { useState, useEffect } from 'react';
import { CloudSun, Thermometer, Zap, Wind, Gauge, Droplets, Compass, Layers3, CheckCircle2, AlertCircle } from 'lucide-react';
import { api } from '@/lib/api';
import { EnvironmentalProfile } from '@/lib/types';
import { MultiSiteComparer } from '@/components/dashboard/MultiSiteComparer';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip } from 'recharts';


export default function EnvironmentPage() {
  const [profile, setProfile] = useState<EnvironmentalProfile | null>(null);

  useEffect(() => {
    api.getEnvironmentProfile(34.1526, 77.5771, "Leh, Ladakh").then(setProfile);
  }, []);

  if (!profile) {
    return <div className="p-8 font-mono text-xs text-gray-400">Loading Environmental Profile...</div>;
  }

  const chartData = [
    { hour: '00:00', temp: profile.minimum_temperature },
    { hour: '04:00', temp: profile.minimum_temperature - 2 },
    { hour: '08:00', temp: profile.average_temperature - 4 },
    { hour: '12:00', temp: profile.maximum_temperature },
    { hour: '16:00', temp: profile.maximum_temperature - 3 },
    { hour: '20:00', temp: profile.average_temperature - 2 },
    { hour: '24:00', temp: profile.minimum_temperature },
  ];

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* HEADER */}
      <div className="bg-[#16171d] border border-[#2e303a] p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="text-[10px] font-mono text-blue-400 font-bold tracking-widest uppercase block mb-1">
            ENVIRONMENTAL & METEOROLOGICAL INTELLIGENCE
          </span>
          <h1 className="text-2xl font-bold text-white tracking-tight m-0 flex items-center gap-3">
            <span>Environment Profile: {profile.location_name}</span>
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Latitude {profile.latitude}°N | Longitude {profile.longitude}°E | Elevation {profile.elevation}m
          </p>
        </div>

        <div className="flex items-center gap-2 font-mono text-xs">
          <span className={`px-3 py-1.5 rounded-xl border font-bold flex items-center gap-2 ${
            profile.data_source === 'LIVE'
              ? 'bg-emerald-950/60 border-emerald-500/50 text-emerald-400'
              : 'bg-amber-950/60 border-amber-500/50 text-amber-400'
          }`}>
            <span className="w-2 h-2 rounded-full bg-current animate-pulse"></span>
            SOURCE: {profile.data_source}
          </span>
        </div>
      </div>

      {/* CLIMATE KPI CARDS GRID */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        <Card icon={<Thermometer className="text-rose-400" />} label="AVG TEMP" value={`${profile.average_temperature}°C`} sub={`Min: ${profile.minimum_temperature}°C | Max: ${profile.maximum_temperature}°C`} />
        <Card icon={<CloudSun className="text-amber-400" />} label="HUMIDITY" value={`${profile.humidity}%`} sub="Relative Moisture" />
        <Card icon={<Zap className="text-yellow-400" />} label="SOLAR RAD" value={`${profile.solar_radiation} W/m²`} sub="Peak Insolation" />
        <Card icon={<Wind className="text-cyan-400" />} label="WIND SPEED" value={`${profile.wind_speed} m/s`} sub={`Dir: ${profile.wind_direction}°`} />
        <Card icon={<Gauge className="text-indigo-400" />} label="PRESSURE" value={`${profile.pressure} hPa`} sub="Surface Level" />
        <Card icon={<Droplets className="text-blue-400" />} label="RAINFALL" value={`${profile.rainfall} mm`} sub="Precipitation" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* HOURLY TEMPERATURE GRAPH */}
        <div className="lg:col-span-7 bg-[#16171d] border border-[#2e303a] p-5 rounded-2xl space-y-4">
          <div className="border-b border-[#2e303a] pb-3">
            <h3 className="text-sm font-bold text-white font-mono uppercase m-0">24-Hour Diurnal Temperature Profile</h3>
            <span className="text-[10px] font-mono text-gray-500">AMBIENT SINK OSCILLATION</span>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="tempGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#f43f5e" stopOpacity={0.4} />
                    <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="hour" stroke="#4b5563" fontSize={11} axisLine={false} tickLine={false} />
                <YAxis stroke="#4b5563" fontSize={11} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#121319', borderColor: '#2e303a', borderRadius: '8px', fontSize: '12px' }} />
                <Area type="monotone" dataKey="temp" stroke="#f43f5e" strokeWidth={2.5} fill="url(#tempGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* SOIL & GEOLOGICAL PROFILE */}
        <div className="lg:col-span-5 bg-[#16171d] border border-[#2e303a] p-5 rounded-2xl space-y-4 font-mono">
          <div className="border-b border-[#2e303a] pb-3 flex items-center gap-2">
            <Layers3 size={18} className="text-emerald-400" />
            <div>
              <h3 className="text-sm font-bold text-white uppercase m-0">Soil & Sub-Surface Intelligence</h3>
              <span className="text-[10px] text-gray-500">THERMAL COUPLING & CONDUCTION</span>
            </div>
          </div>

          <div className="bg-[#121319] border border-[#2e303a] p-4 rounded-xl space-y-3">
            <div className="flex justify-between items-center text-xs">
              <span className="text-gray-400">SOIL CLASSIFICATION</span>
              <strong className="text-emerald-400 font-bold">{profile.soil_properties.soil_type}</strong>
            </div>

            <div className="space-y-2 pt-2 border-t border-[#222530] text-xs">
              <div className="flex justify-between text-gray-400">
                <span>SAND / CLAY / SILT RATIO</span>
                <span className="text-white">{profile.soil_properties.sand_percentage}% / {profile.soil_properties.clay_percentage}% / {profile.soil_properties.silt_percentage}%</span>
              </div>
              <div className="w-full bg-[#1e202a] h-2 rounded-full overflow-hidden flex">
                <div className="bg-amber-600 h-full" style={{ width: `${profile.soil_properties.sand_percentage}%` }}></div>
                <div className="bg-rose-600 h-full" style={{ width: `${profile.soil_properties.clay_percentage}%` }}></div>
                <div className="bg-blue-600 h-full" style={{ width: `${profile.soil_properties.silt_percentage}%` }}></div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 pt-2 text-xs">
              <div className="bg-[#181a22] p-2.5 rounded-lg border border-[#2e303a]">
                <span className="text-[10px] text-gray-500 block">MOISTURE CONTENT</span>
                <strong className="text-white text-sm">{profile.soil_properties.moisture_content * 100}%</strong>
              </div>
              <div className="bg-[#181a22] p-2.5 rounded-lg border border-[#2e303a]">
                <span className="text-[10px] text-gray-500 block">THERMAL COND.</span>
                <strong className="text-blue-400 text-sm">{profile.soil_properties.thermal_conductivity} W/m·K</strong>
              </div>
            </div>
          </div>
        </div>
      </div>
      {/* MULTI-SITE COMPARISON ENGINE */}
      <div className="pt-4">
        <MultiSiteComparer />
      </div>
    </div>
  );
}


function Card({ icon, label, value, sub }: { icon: React.ReactNode; label: string; value: string; sub: string }) {
  return (
    <div className="bg-[#16171d] border border-[#2e303a] p-4 rounded-2xl space-y-2">
      <div className="w-8 h-8 rounded-lg bg-[#121319] border border-[#2e303a] flex items-center justify-center">
        {icon}
      </div>
      <div>
        <span className="text-[10px] font-mono text-gray-500 block uppercase">{label}</span>
        <strong className="text-lg font-bold font-mono text-white block">{value}</strong>
        <span className="text-[9px] text-gray-400 block">{sub}</span>
      </div>
    </div>
  );
}
