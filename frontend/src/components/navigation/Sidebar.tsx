'use client';
import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Gauge,
  CloudSun,
  SlidersHorizontal,
  Box,
  BrainCircuit,
  Cpu,
  Bot,
  Thermometer,
  Moon
} from 'lucide-react';

const navItems = [
  { name: 'Dashboard Home', href: '/', icon: Gauge },
  { name: 'Design Analysis', href: '/design', icon: SlidersHorizontal },
  { name: 'Environment Profile', href: '/environment', icon: CloudSun },
  { name: 'Optimization Results', href: '/results', icon: Box },
  { name: 'Surrogate ML Model', href: '/model', icon: BrainCircuit },
  { name: 'ANSYS Simulation', href: '/simulation', icon: Cpu },
  { name: 'AI Assistant', href: '/assistant', icon: Bot },
];

export const Sidebar: React.FC = () => {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-[#0b131f] border-r border-[#1b2f48] flex flex-col h-screen shrink-0 sticky top-0 font-sans">
      {/* BRAND */}
      <div className="p-5 border-b border-[#1b2f48] flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-[#064789]/30 border border-[#427AA1]/50 flex items-center justify-center text-[#427AA1]">
          <Thermometer size={20} />
        </div>
        <div>
          <h1 className="text-sm font-extrabold tracking-wider text-[#EBF2FA] m-0 uppercase font-mono">CLIMATESHELTER AI</h1>
          <span className="text-[10px] text-[#427AA1] font-mono tracking-widest block uppercase">ENGINEERING PLATFORM</span>
        </div>
      </div>

      {/* NAV LIST */}
      <div className="p-4 flex-1 overflow-y-auto">
        <span className="text-[10px] font-mono text-gray-500 tracking-wider uppercase mb-3 block px-2">
          CORE WORKSPACE
        </span>

        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-[#064789]/30 text-[#EBF2FA] border border-[#427AA1]/50 shadow-sm font-bold'
                    : 'text-gray-400 hover:text-white hover:bg-[#101c2c]'
                }`}
              >
                <Icon size={16} className={isActive ? 'text-[#A5BE00]' : 'text-gray-400'} />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* SYSTEM STATUS CARD */}
      <div className="p-4 border-t border-[#1b2f48] space-y-3">
        <div className="p-3 rounded-lg bg-[#101c2c] border border-[#1b2f48] text-xs font-mono space-y-2">
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-1.5 text-[#679436] font-bold text-[11px]">
              <span className="w-2 h-2 rounded-full bg-[#679436] animate-pulse"></span>
              SYSTEM ONLINE
            </span>
            <span className="text-[10px] text-gray-400">v1.0.0</span>
          </div>

          <div className="flex justify-between text-[11px] text-gray-400 pt-1 border-t border-[#1b2f48]">
            <span>ANSYS ADAPTER</span>
            <strong className="text-[#A5BE00] font-normal">MOCK READY</strong>
          </div>
          <div className="flex justify-between text-[11px] text-gray-400">
            <span>ML SURROGATE</span>
            <strong className="text-[#427AA1] font-normal">R² 0.968</strong>
          </div>
        </div>

        <div className="flex items-center justify-between px-2 text-xs text-gray-400">
          <div className="flex items-center gap-2">
            <Moon size={14} />
            <span>Theme</span>
          </div>
          <span className="text-[10px] font-mono text-[#EBF2FA] bg-[#064789] border border-[#427AA1] px-2 py-0.5 rounded font-bold">PALETTE ACTIVE</span>
        </div>
      </div>
    </aside>
  );
};
