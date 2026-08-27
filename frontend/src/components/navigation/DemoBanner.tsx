'use client';
import React from 'react';
import { AlertTriangle, Info, CheckCircle2 } from 'lucide-react';

interface DemoBannerProps {
  mode?: string;
  source?: string;
}

export const DemoBanner: React.FC<DemoBannerProps> = ({ mode = "DEMO MODE", source = "MOCK / ADAPTER" }) => {
  return (
    <div className="bg-amber-950/40 border-b border-amber-500/30 text-amber-200 px-4 py-2 text-xs font-mono flex items-center justify-between z-50">
      <div className="flex items-center gap-2">
        <AlertTriangle size={15} className="text-amber-400 shrink-0" />
        <span className="font-bold text-amber-400 uppercase tracking-wider">{mode}</span>
        <span className="hidden md:inline text-amber-300/80">
          — External ANSYS execution & Live API fallback adapters active. All mock data is clearly labeled.
        </span>
      </div>

      <div className="flex items-center gap-3 text-[11px]">
        <span className="flex items-center gap-1.5 bg-amber-900/50 px-2 py-0.5 rounded border border-amber-600/30">
          <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse"></span>
          SOURCE: {source}
        </span>
        <span className="hidden sm:inline-block text-amber-400/60">
          Set environment keys to switch to LIVE
        </span>
      </div>
    </div>
  );
};
