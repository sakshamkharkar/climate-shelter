'use client';
import React, { useState } from 'react';
import { MapPin, ChevronDown, Bell, Settings, Search, Check } from 'lucide-react';
import { api } from '@/lib/api';
import { LocationSearchResult } from '@/lib/types';

interface HeaderProps {
  currentLocation: string;
  onLocationSelect: (loc: LocationSearchResult) => void;
}

export const Header: React.FC<HeaderProps> = ({ currentLocation, onLocationSelect }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState<LocationSearchResult[]>([
    { name: "Leh, Ladakh", latitude: 34.1526, longitude: 77.5771, country: "India", elevation: 3500 },
    { name: "Cairo, Egypt", latitude: 30.0444, longitude: 31.2357, country: "Egypt", elevation: 23 },
    { name: "Reykjavik, Iceland", latitude: 64.1466, longitude: -21.9426, country: "Iceland", elevation: 15 },
    { name: "Phoenix, Arizona", latitude: 33.4484, longitude: -112.0740, country: "United States", elevation: 331 },
    { name: "La Paz, Bolivia", latitude: -16.5000, longitude: -68.1500, country: "Bolivia", elevation: 3640 }
  ]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    const res = await api.searchLocation(searchQuery);
    if (res.length > 0) {
      setResults(res);
    }
  };

  return (
    <header className="h-16 border-b border-[#1b2f48] bg-[#0b131f] px-6 flex items-center justify-between z-40 sticky top-0 font-sans">
      {/* LOCATION PICKER */}
      <div className="relative">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center gap-3 px-3 py-1.5 rounded-lg bg-[#101c2c] border border-[#1b2f48] hover:border-[#427AA1] transition-all text-left"
        >
          <div className="w-7 h-7 rounded-md bg-[#064789]/30 text-[#427AA1] flex items-center justify-center">
            <MapPin size={16} />
          </div>
          <div>
            <span className="text-[10px] font-mono text-gray-400 block leading-tight">LOCATION</span>
            <span className="text-xs font-semibold text-[#EBF2FA]">{currentLocation}</span>
          </div>
          <ChevronDown size={14} className="text-gray-400 ml-1" />
        </button>

        {isOpen && (
          <div className="absolute top-12 left-0 w-72 bg-[#101c2c] border border-[#1b2f48] rounded-xl shadow-2xl p-3 z-50">
            <form onSubmit={handleSearch} className="flex gap-2 mb-3">
              <div className="relative flex-1">
                <Search size={14} className="absolute left-2.5 top-2.5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search city (e.g. Cairo)..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-[#0b131f] border border-[#1b2f48] rounded-lg pl-8 pr-3 py-1.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-[#427AA1]"
                />
              </div>
              <button type="submit" className="bg-[#064789] hover:bg-[#427AA1] text-white text-xs px-3 py-1.5 rounded-lg font-bold">
                Go
              </button>
            </form>

            <div className="space-y-1 max-h-48 overflow-y-auto">
              {results.map((loc) => (
                <button
                  key={loc.name}
                  onClick={() => {
                    onLocationSelect(loc);
                    setIsOpen(false);
                  }}
                  className="w-full text-left px-3 py-2 rounded-lg text-xs hover:bg-[#1b2f48] flex items-center justify-between text-gray-300 hover:text-white"
                >
                  <div>
                    <span className="font-medium block">{loc.name}</span>
                    <span className="text-[10px] text-gray-400 font-mono">
                      {loc.latitude.toFixed(2)}°, {loc.longitude.toFixed(2)}°
                    </span>
                  </div>
                  {currentLocation === loc.name && <Check size={14} className="text-[#A5BE00]" />}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* TOP STATUS BADGES */}
      <div className="hidden lg:flex items-center gap-4 text-xs font-mono">
        <div className="flex items-center gap-2 bg-[#101c2c] border border-[#1b2f48] px-3 py-1 rounded-md">
          <span className="w-2 h-2 rounded-full bg-[#A5BE00] animate-pulse"></span>
          <span className="text-gray-400">ML SURROGATE:</span>
          <strong className="text-[#A5BE00] font-medium">ACTIVE</strong>
        </div>

        <div className="flex items-center gap-2 bg-[#101c2c] border border-[#1b2f48] px-3 py-1 rounded-md">
          <span className="w-2 h-2 rounded-full bg-[#679436]"></span>
          <span className="text-gray-400">ANSYS SOLVER:</span>
          <strong className="text-[#679436] font-medium">ADAPTER READY</strong>
        </div>
      </div>

      {/* TOP ACTIONS */}
      <div className="flex items-center gap-3">
        <div className="hidden sm:block text-right font-mono text-xs pr-3 border-r border-[#1b2f48]">
          <span className="text-[10px] text-gray-400 block">RUN ID</span>
          <strong className="text-[#EBF2FA]">TR-00451-B</strong>
        </div>

        <button className="w-9 h-9 rounded-lg bg-[#101c2c] border border-[#1b2f48] flex items-center justify-center text-gray-400 hover:text-white hover:border-[#427AA1] transition-all">
          <Bell size={16} />
        </button>

        <button className="w-9 h-9 rounded-lg bg-[#101c2c] border border-[#1b2f48] flex items-center justify-center text-gray-400 hover:text-white hover:border-[#427AA1] transition-all">
          <Settings size={16} />
        </button>

        <div className="w-9 h-9 rounded-lg bg-[#064789] border border-[#427AA1] flex items-center justify-center font-mono text-xs font-bold text-[#EBF2FA]">
          CS
        </div>
      </div>
    </header>
  );
};
