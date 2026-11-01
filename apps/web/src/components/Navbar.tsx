"use client";

import React, { useState } from "react";
import {
  Activity,
  BrainCircuit,
  Compass,
  FileSpreadsheet,
  Layers,
  MapPin,
  Menu,
  PieChart,
  Receipt,
  Search,
  Settings,
  TrendingUp,
  X,
  Zap,
} from "lucide-react";

export type NavTab =
  | "overview"
  | "earnings"
  | "prediction"
  | "deliveries"
  | "demand"
  | "platforms"
  | "recommendations"
  | "expenses"
  | "imports"
  | "models"
  | "settings";

interface NavbarProps {
  currentTab: NavTab;
  onSelectTab: (tab: NavTab) => void;
  workerRef: string;
  onSelectWorker: (workerRef: string) => void;
  workers: Array<{ worker_ref: string; display_name: string }>;
  isExpanded?: boolean;
  onToggleExpand?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  onSelectTab,
  workerRef,
  onSelectWorker,
  workers,
}) => {
  const [mobileOpen, setMobileOpen] = useState(false);

  const navItems: Array<{ id: NavTab; label: string; icon: React.ReactNode; badge?: string }> = [
    { id: "overview", label: "Operations Cockpit", icon: <Layers className="w-4 h-4" /> },
    { id: "earnings", label: "Earnings Analytics", icon: <TrendingUp className="w-4 h-4" /> },
    { id: "prediction", label: "Earnings Predictor", icon: <Zap className="w-4 h-4" />, badge: "AI" },
    { id: "deliveries", label: "Delivery Activity", icon: <Activity className="w-4 h-4" /> },
    { id: "demand", label: "Zone Demand Forecast", icon: <MapPin className="w-4 h-4" />, badge: "Lag" },
    { id: "platforms", label: "Platform Benchmark", icon: <PieChart className="w-4 h-4" /> },
    { id: "recommendations", label: "Opportunity Planner", icon: <Compass className="w-4 h-4" />, badge: "Opt" },
    { id: "expenses", label: "Operating Expenses", icon: <Receipt className="w-4 h-4" /> },
    { id: "imports", label: "Data Pipeline", icon: <FileSpreadsheet className="w-4 h-4" /> },
    { id: "models", label: "Model Registry Lab", icon: <BrainCircuit className="w-4 h-4" /> },
    { id: "settings", label: "Worker & Governance", icon: <Settings className="w-4 h-4" /> },
  ];

  return (
    <>
      {/* Mobile Top Navigation Toggle */}
      <div className="md:hidden flex items-center justify-between px-4 py-3 bg-surface-1 border-b border-hairline">
        <div className="flex items-center space-x-2.5">
          <div className="w-7 h-7 rounded-lg bg-surface-raised border border-hairline flex items-center justify-center">
            {/* Custom SVG logo mark in acid-lime */}
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" className="text-lime">
              <path d="M4 6h16M4 12h12M4 18h8" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
            </svg>
          </div>
          <span className="font-bold text-sm tracking-tight text-content-primary">GigPulse AI</span>
        </div>
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="p-1.5 rounded-lg bg-surface-2 border border-hairline text-content-secondary hover:text-content-primary"
        >
          {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>

      {/* Mobile Drawer */}
      {mobileOpen && (
        <div className="md:hidden fixed inset-0 z-40 bg-canvas/90 backdrop-blur-md pt-16 px-4 pb-6 overflow-y-auto">
          <div className="mb-4 p-3 bg-surface-1 rounded-xl border border-hairline">
            <label className="text-[10px] uppercase font-semibold text-content-muted tracking-wider block mb-1.5">
              Active Worker
            </label>
            <select
              value={workerRef}
              onChange={(e) => {
                onSelectWorker(e.target.value);
                setMobileOpen(false);
              }}
              className="w-full bg-surface-2 border border-hairline rounded-lg px-3 py-2 text-xs text-content-primary focus:outline-none focus:border-lime"
            >
              {workers.map((w) => (
                <option key={w.worker_ref} value={w.worker_ref}>
                  {w.display_name} ({w.worker_ref})
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-1">
            {navItems.map((item) => {
              const isActive = currentTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    onSelectTab(item.id);
                    setMobileOpen(false);
                  }}
                  className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all ${
                    isActive
                      ? "bg-surface-raised text-lime border border-lime/30 shadow-lime-sm"
                      : "text-content-secondary hover:text-content-primary hover:bg-surface-1"
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <span className={isActive ? "text-lime" : "text-content-muted"}>{item.icon}</span>
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-surface-2 text-content-muted border border-hairline">
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Desktop Vertical Icon Rail (Matching Target Reference) */}
      <aside className="hidden md:flex flex-col items-center justify-between w-18 py-5 bg-surface-1 border-r border-hairline shrink-0 z-30 select-none">
        {/* Brand Logo Mark */}
        <div className="flex flex-col items-center space-y-4">
          <div
            title="GigPulse AI Operations Cockpit"
            className="w-10 h-10 rounded-xl bg-canvas border border-hairline flex items-center justify-center cursor-pointer hover:border-lime/40 transition-colors group"
            onClick={() => onSelectTab("overview")}
          >
            {/* Target screenshot logo glyph: layered acid-lime bars */}
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" className="text-lime group-hover:scale-105 transition-transform">
              <path d="M4 5h16M4 11h11M4 17h7" stroke="currentColor" strokeWidth="3.2" strokeLinecap="round" />
            </svg>
          </div>

          {/* Navigation Icon Stack */}
          <nav className="flex flex-col items-center space-y-2 pt-2">
            {navItems.slice(0, 7).map((item) => {
              const isActive = currentTab === item.id;
              return (
                <div key={item.id} className="relative group">
                  <button
                    onClick={() => onSelectTab(item.id)}
                    aria-label={item.label}
                    className={`w-11 h-11 rounded-2xl flex items-center justify-center transition-all duration-200 relative ${
                      isActive
                        ? "bg-surface-raised text-lime border border-lime/30 shadow-lime-sm"
                        : "text-content-muted hover:text-content-primary hover:bg-surface-2"
                    }`}
                  >
                    <span className="transition-transform group-hover:scale-110">{item.icon}</span>
                    {isActive && (
                      <span className="absolute -left-1 w-1 h-3.5 bg-lime rounded-r-full shadow-lime-glow" />
                    )}
                  </button>

                  {/* Sleek Dark Hover Tooltip */}
                  <div className="absolute left-14 top-1/2 -translate-y-1/2 hidden group-hover:flex items-center z-50 pointer-events-none">
                    <div className="bg-surface-2 text-content-primary text-xs font-medium px-2.5 py-1.5 rounded-lg border border-hairline shadow-card whitespace-nowrap flex items-center space-x-2">
                      <span>{item.label}</span>
                      {item.badge && (
                        <span className="text-[9px] px-1 py-0.2 bg-lime-muted text-lime rounded border border-lime/30">
                          {item.badge}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </nav>
        </div>

        {/* Bottom Rail Secondary Actions */}
        <div className="flex flex-col items-center space-y-2 pt-4 border-t border-hairline/60 w-full px-3">
          {navItems.slice(7).map((item) => {
            const isActive = currentTab === item.id;
            return (
              <div key={item.id} className="relative group">
                <button
                  onClick={() => onSelectTab(item.id)}
                  aria-label={item.label}
                  className={`w-11 h-11 rounded-2xl flex items-center justify-center transition-all duration-200 relative ${
                    isActive
                      ? "bg-surface-raised text-lime border border-lime/30 shadow-lime-sm"
                      : "text-content-muted hover:text-content-primary hover:bg-surface-2"
                  }`}
                >
                  <span className="transition-transform group-hover:scale-110">{item.icon}</span>
                  {isActive && (
                    <span className="absolute -left-1 w-1 h-3.5 bg-lime rounded-r-full shadow-lime-glow" />
                  )}
                </button>

                <div className="absolute left-14 top-1/2 -translate-y-1/2 hidden group-hover:flex items-center z-50 pointer-events-none">
                  <div className="bg-surface-2 text-content-primary text-xs font-medium px-2.5 py-1.5 rounded-lg border border-hairline shadow-card whitespace-nowrap">
                    {item.label}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </aside>
    </>
  );
};
