'use client';
import React, { useState } from 'react';
import { Plus, Trash2, MapPin, Layers3, BarChart2, Compass, Play, Sparkles, CheckCircle2 } from 'lucide-react';
import { api } from '@/lib/api';
import { SiteCoordinate, SiteOptimizationResult, EnvironmentalProfile } from '@/lib/types';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';

export const MultiSiteComparer: React.FC = () => {
  const [sites, setSites] = useState<SiteCoordinate[]>([
    { id: '1', name: 'Site A: Leh, Ladakh', latitude: 34.1526, longitude: 77.5771 },
    { id: '2', name: 'Site B: Cairo, Egypt', latitude: 30.0444, longitude: 31.2357 },
    { id: '3', name: 'Site C: Reykjavik, Iceland', latitude: 64.1466, longitude: -21.9426 },
  ]);

  const [profiles, setProfiles] = useState<EnvironmentalProfile[]>([]);
  const [optResults, setOptResults] = useState<SiteOptimizationResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const addSite = () => {
    const nextNum = sites.length + 1;
    setSites([
      ...sites,
      {
        id: Date.now().toString(),
        name: `Site ${String.fromCharCode(64 + nextNum)}: New Coordinates`,
        latitude: 25.0,
        longitude: 45.0,
      },
    ]);
  };

  const removeSite = (id: string) => {
    if (sites.length <= 1) return;
    setSites(sites.filter((s) => s.id !== id));
  };

  const updateSite = (id: string, field: keyof SiteCoordinate, value: any) => {
    setSites(
      sites.map((s) => (s.id === id ? { ...s, [field]: value } : s))
    );
  };

  const handleSiteNameChange = async (id: string, nameValue: string) => {
    // Update name immediately
    updateSite(id, 'name', nameValue);

    // Auto lookup coordinates if 3+ characters typed
    if (nameValue.trim().length >= 3) {
      try {
        const results = await api.searchLocation(nameValue);
        if (results && results.length > 0) {
          const topMatch = results[0];
          setSites((prevSites) =>
            prevSites.map((s) =>
              s.id === id
                ? {
                    ...s,
                    latitude: topMatch.latitude,
                    longitude: topMatch.longitude,
                  }
                : s
            )
          );
        }
      } catch (err) {
        console.warn("Geocoding lookup failed:", err);
      }
    }
  };


  const handleCompare = async () => {
    setIsLoading(true);
    try {
      const siteInputs = sites.map((s) => ({
        name: s.name,
        latitude: parseFloat(s.latitude as any) || 0,
        longitude: parseFloat(s.longitude as any) || 0,
      }));

      const profs = await api.getMultiSiteProfiles(siteInputs);
      setProfiles(profs);

      const opts = await api.runMultiSiteOptimization(siteInputs);
      setOptResults(opts);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const chartData = optResults.map((r) => ({
    name: r.site_name,
    OutdoorTemp: r.outdoor_avg_temp,
    IndoorPredictedTemp: r.predicted_interior_temp,
  }));

  return (
    <div className="bg-[#101c2c] border border-[#1b2f48] p-6 rounded-2xl space-y-6 font-sans">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#1b2f48] pb-4">
        <div>
          <span className="text-[10px] font-mono text-[#A5BE00] font-bold tracking-widest uppercase block mb-1">
            MULTI-SITE COORDINATE COMPARISON ENGINE
          </span>
          <h2 className="text-xl font-bold text-[#EBF2FA] tracking-tight m-0 flex items-center gap-2">
            <Compass size={20} className="text-[#427AA1]" />
            <span>Multiple Site Input & Comparative Analysis</span>
          </h2>
          <p className="text-xs text-gray-300 mt-1">
            Input multiple site latitude & longitude coordinates to compare micro-climates, soil properties, and optimal shelter configurations side-by-side.
          </p>
        </div>

        <button
          onClick={handleCompare}
          disabled={isLoading}
          className="flex items-center justify-center gap-2 bg-[#064789] hover:bg-[#427AA1] text-white font-mono text-xs font-medium px-5 py-2.5 rounded-xl border border-[#427AA1] shadow-lg transition-all uppercase shrink-0"
        >
          <Play size={14} className={isLoading ? "animate-spin" : ""} />
          <span>{isLoading ? "Analyzing Multi-Sites..." : "Run Multi-Site Comparison"}</span>
        </button>
      </div>


      {/* SITES INPUT GRID */}
      <div className="space-y-3">
        <div className="flex justify-between items-center text-xs font-mono text-gray-400">
          <span>CONFIGURE SITE COORDINATES ({sites.length} SITES)</span>
          <button
            onClick={addSite}
            className="flex items-center gap-1 text-blue-400 hover:text-blue-300 font-semibold text-xs"
          >
            <Plus size={14} /> Add Another Site Coordinate
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {sites.map((site, index) => (
            <div key={site.id} className="bg-[#121319] border border-[#2e303a] p-4 rounded-xl space-y-3 relative font-mono">
              <div className="flex justify-between items-center">
                <span className="text-[10px] text-blue-400 font-bold">SITE #{index + 1}</span>
                {sites.length > 1 && (
                  <button onClick={() => removeSite(site.id)} className="text-gray-500 hover:text-rose-400">
                    <Trash2 size={14} />
                  </button>
                )}
              </div>

              <div>
                <label className="text-[9px] text-gray-500 block uppercase mb-1">SITE NAME / LABEL</label>
                <input
                  type="text"
                  value={site.name}
                  onChange={(e) => handleSiteNameChange(site.id, e.target.value)}
                  className="w-full bg-[#181a22] border border-[#2e303a] rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[9px] text-gray-500 block uppercase mb-1">LATITUDE (°N)</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={site.latitude}
                    onChange={(e) => updateSite(site.id, 'latitude', e.target.value)}
                    className="w-full bg-[#181a22] border border-[#2e303a] rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="text-[9px] text-gray-500 block uppercase mb-1">LONGITUDE (°E)</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={site.longitude}
                    onChange={(e) => updateSite(site.id, 'longitude', e.target.value)}
                    className="w-full bg-[#181a22] border border-[#2e303a] rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* COMPARISON RESULTS */}
      {optResults.length > 0 && (
        <div className="space-y-6 pt-4 border-t border-[#2e303a]">
          {/* COMPARISON CHART */}
          <div className="bg-[#121319] border border-[#2e303a] p-5 rounded-xl space-y-3 font-mono">
            <div className="flex justify-between items-center">
              <h3 className="text-xs font-bold text-white uppercase m-0">Outdoor vs Indoor Predicted Temperature Across Multi-Sites</h3>
              <span className="text-[10px] text-gray-400">ML SURROGATE COMPARISON</span>
            </div>

            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <XAxis dataKey="name" stroke="#4b5563" fontSize={10} axisLine={false} tickLine={false} />
                  <YAxis stroke="#4b5563" fontSize={10} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={{ backgroundColor: '#121319', borderColor: '#2e303a', borderRadius: '8px', fontSize: '12px' }} />
                  <Legend />
                  <Bar dataKey="OutdoorTemp" fill="#6b7280" radius={[4, 4, 0, 0]} name="Outdoor Avg Temp (°C)" />
                  <Bar dataKey="IndoorPredictedTemp" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Indoor Predicted Temp (°C)" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* SIDE BY SIDE CARDS */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {optResults.map((r, idx) => (
              <div key={idx} className="bg-[#121319] border border-[#2e303a] p-4 rounded-xl space-y-3 font-mono text-xs">
                <div className="flex items-center justify-between border-b border-[#222530] pb-2">
                  <strong className="text-white text-xs">{r.site_name}</strong>
                  <span className="text-[9px] text-gray-500">{r.latitude.toFixed(2)}°, {r.longitude.toFixed(2)}°</span>
                </div>

                <div className="space-y-1.5 text-[11px]">
                  <div className="flex justify-between text-gray-400">
                    <span>OUTDOOR AVG:</span>
                    <strong className="text-rose-400">{r.outdoor_avg_temp}°C</strong>
                  </div>
                  <div className="flex justify-between text-gray-400">
                    <span>INDOOR PREDICTED:</span>
                    <strong className="text-blue-400 font-bold">{r.predicted_interior_temp}°C</strong>
                  </div>
                  <div className="flex justify-between text-gray-400 pt-1 border-t border-[#222530]">
                    <span>BEST MATERIAL:</span>
                    <strong className="text-emerald-400">{r.best_design.material_name.split(' ')[0]}</strong>
                  </div>
                  <div className="flex justify-between text-gray-400">
                    <span>WALL THICKNESS:</span>
                    <strong className="text-white">{r.best_design.parameters.wall_thickness} m</strong>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
