'use client';
import React, { useState, useEffect } from 'react';
import './globals.css';
import { Sidebar } from '@/components/navigation/Sidebar';
import { Header } from '@/components/navigation/Header';
import { DemoBanner } from '@/components/navigation/DemoBanner';
import { LocationSearchResult } from '@/lib/types';
import { api } from '@/lib/api';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const [currentLocation, setCurrentLocation] = useState<LocationSearchResult>({
    name: 'Leh, Ladakh',
    latitude: 34.1526,
    longitude: 77.5771,
    country: 'India',
    elevation: 3500
  });

  const [isDemoMode, setIsDemoMode] = useState(true);

  useEffect(() => {
    api.getHealth().then((data) => {
      setIsDemoMode(data.demo_mode ?? true);
    });
  }, []);

  return (
    <html lang="en" className="dark">
      <head>
        <title>ClimateShelter AI — Climate-Aware Thermal Design Platform</title>
        <meta name="description" content="Intelligent shelter design, ML surrogate modeling, and ANSYS validation" />
      </head>
      <body className="bg-[#0f1015] text-[#f3f4f6] font-sans min-h-screen flex flex-col antialiased">
        <DemoBanner mode={isDemoMode ? "DEMO MODE — Fallback Adapters Active" : "LIVE MODE — Connected"} source="OPEN-METEO & ANSYS ADAPTER" />
        
        <div className="flex flex-1 min-h-0">
          <Sidebar />
          
          <div className="flex-1 flex flex-col min-w-0">
            <Header
              currentLocation={currentLocation.name}
              onLocationSelect={(loc) => setCurrentLocation(loc)}
            />
            
            <main className="flex-1 p-6 overflow-y-auto bg-[#0f1015]">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}
