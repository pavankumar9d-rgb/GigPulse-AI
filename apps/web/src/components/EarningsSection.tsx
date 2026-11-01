"use client";

import React, { useState } from "react";
import {
  Calendar,
  Filter,
  IndianRupee,
  Layers,
  ShieldCheck,
  TrendingDown,
  TrendingUp,
} from "lucide-react";
import { AnimatedNumber } from "./AnimatedCounter";
import { DEMO_SUMMARY } from "../lib/demoData";

interface EarningsSectionProps {
  summary: any;
  earningsHistory: any[];
  deliveries: any[];
  weeklySummary?: any;
}

export const EarningsSection: React.FC<EarningsSectionProps> = ({
  summary,
  earningsHistory,
  deliveries,
  weeklySummary,
}) => {
  const [viewMode, setViewMode] = useState<"net" | "gross">("net");
  const [platformFilter, setPlatformFilter] = useState<string>("all");

  const analytics = summary?.analytics || DEMO_SUMMARY.analytics;
  const earnings = analytics?.earnings || DEMO_SUMMARY.analytics.earnings;

  // Filter deliveries
  const filteredDeliveries = deliveries.filter((d) =>
    platformFilter === "all" ? true : d.platform_code === platformFilter
  );

  return (
    <div className="p-5 md:p-8 space-y-6 max-w-[1600px] mx-auto select-none">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-content-primary flex items-center space-x-2">
            <span>Earnings Analytics & Net Income Ledger</span>
          </h2>
          <p className="text-xs text-content-muted mt-0.5">
            Verified breakdown of gross payouts, incentives, tips, and operational deductions in integer paise
          </p>
        </div>

        {/* View Toggles & Filters */}
        <div className="flex items-center space-x-3">
          <div className="bg-surface-1 border border-hairline p-1 rounded-full flex items-center text-xs shadow-card">
            <button
              onClick={() => setViewMode("net")}
              className={`px-3.5 py-1 rounded-full font-medium transition-all ${
                viewMode === "net"
                  ? "bg-lime text-canvas font-bold shadow-lime-sm"
                  : "text-content-muted hover:text-content-primary"
              }`}
            >
              Net Income
            </button>
            <button
              onClick={() => setViewMode("gross")}
              className={`px-3.5 py-1 rounded-full font-medium transition-all ${
                viewMode === "gross"
                  ? "bg-lime text-canvas font-bold shadow-lime-sm"
                  : "text-content-muted hover:text-content-primary"
              }`}
            >
              Gross Payout
            </button>
          </div>

          <div className="flex items-center space-x-1.5 bg-surface-1 border border-hairline px-3 py-1.5 rounded-full text-xs text-content-secondary shadow-card">
            <Filter className="w-3.5 h-3.5 text-content-muted" />
            <select
              value={platformFilter}
              onChange={(e) => setPlatformFilter(e.target.value)}
              className="bg-transparent text-content-primary focus:outline-none cursor-pointer"
            >
              <option value="all" className="bg-surface-1">All Platforms</option>
              <option value="flash_drop" className="bg-surface-1">FlashDrop</option>
              <option value="swift_bite" className="bg-surface-1">SwiftBite</option>
              <option value="hyper_courier" className="bg-surface-1">HyperCourier</option>
            </select>
          </div>
        </div>
      </div>

      {/* Metric Cards Summary */}
      {(() => {
        const grossVal = earnings?.gross_paise
          ? earnings.gross_paise / 100
          : parseFloat(String(earnings?.gross_formatted || "0").replace(/[^0-9.]/g, "")) || 0;
        const expVal = earnings?.total_expenses_paise
          ? earnings.total_expenses_paise / 100
          : parseFloat(String(earnings?.total_expenses_formatted || "0").replace(/[^0-9.]/g, "")) || 0;
        const netVal = earnings?.net_paise
          ? earnings.net_paise / 100
          : parseFloat(String(earnings?.net_formatted || "0").replace(/[^0-9.]/g, "")) || 0;

        return (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div className="bg-surface-1 border border-hairline rounded-2xl p-5 shadow-card relative overflow-hidden">
              <div className="flex items-center justify-between text-content-muted text-xs">
                <span className="uppercase tracking-wider font-semibold text-[10px]">Gross Payout</span>
                <IndianRupee className="w-4 h-4 text-content-secondary" />
              </div>
              <div className="text-3xl font-bold font-mono text-content-primary mt-2">
                <AnimatedNumber value={grossVal} prefix="₹" decimals={2} duration={1200} />
              </div>
              <span className="text-[11px] text-content-muted mt-2 block">
                Base payouts + platform incentives + direct tips
              </span>
            </div>

            <div className="bg-surface-1 border border-hairline rounded-2xl p-5 shadow-card relative overflow-hidden">
              <div className="flex items-center justify-between text-content-muted text-xs">
                <span className="uppercase tracking-wider font-semibold text-[10px]">Operating Deductions</span>
                <TrendingDown className="w-4 h-4 text-semantic-red" />
              </div>
              <div className="text-3xl font-bold font-mono text-semantic-red mt-2">
                <AnimatedNumber value={expVal} prefix="₹" decimals={2} duration={1200} />
              </div>
              <span className="text-[11px] text-content-muted mt-2 block">
                Fuel consumption, vehicle wear, mobile data
              </span>
            </div>

            <div className="bg-surface-1 border border-hairline rounded-2xl p-5 shadow-card relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-lime/5 rounded-full blur-2xl pointer-events-none" />
              <div className="flex items-center justify-between text-xs">
                <span className="uppercase tracking-wider font-bold text-[10px] text-lime">Worker Net Take-Home</span>
                <ShieldCheck className="w-4 h-4 text-lime" />
              </div>
              <div className="text-3xl font-bold font-mono text-lime mt-2">
                <AnimatedNumber value={netVal} prefix="₹" decimals={2} duration={1200} />
              </div>
              <span className="text-[11px] text-content-muted mt-2 block">
                True bottom-line earnings after deducting verified expenses
              </span>
            </div>
          </div>
        );
      })()}

      {/* Rolling 7-Completed-Calendar-Day Window & Today In Progress */}
      {weeklySummary && (
        <div className="bg-surface-1 border border-hairline rounded-2xl p-5 shadow-card">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-hairline">
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-xs font-semibold tracking-tight text-content-primary">
                  Rolling 7-Completed-Day Window
                </h3>
                <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-indigo-950/60 text-indigo-400 border border-indigo-400/30 uppercase font-bold">
                  DATABASE DATA
                </span>
              </div>
              <p className="text-[10px] text-content-muted font-mono mt-0.5">
                Completed: {weeklySummary.completed_window?.start_date} to {weeklySummary.completed_window?.end_date} (Asia/Kolkata) • strictly excludes today
              </p>
            </div>
            <div className="flex items-center space-x-4 text-xs font-mono">
              <div>
                <span className="text-[10px] text-content-muted block">7-Day Gross</span>
                <span className="font-bold text-content-primary">{weeklySummary.totals?.completed_gross_inr}</span>
              </div>
              <div>
                <span className="text-[10px] text-content-muted block">7-Day Net</span>
                <span className="font-bold text-lime">{weeklySummary.totals?.completed_net_inr}</span>
              </div>
            </div>
          </div>

          {/* 7 Completed Days Horizontal Strip */}
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2.5 pt-4">
            {weeklySummary.completed_days?.map((d: any) => (
              <div
                key={d.date}
                className="bg-surface-2 border border-hairline/80 rounded-xl p-3 text-center space-y-1 hover:border-lime/30 transition-all"
              >
                <div className="text-[10px] font-mono text-content-muted uppercase">
                  {d.day_name} • {d.date.slice(5)}
                </div>
                <div className="text-xs font-mono font-bold text-content-primary">
                  {d.gross_inr}
                </div>
                <div className="text-[9px] text-lime font-mono">
                  Net {d.net_inr}
                </div>
                <div className="text-[9px] text-content-muted">
                  {d.delivery_count} trips
                </div>
              </div>
            ))}
          </div>

          {/* Separate Today In-Progress Banner */}
          {weeklySummary.today_in_progress && (
            <div className="mt-4 p-3 bg-surface-2/60 border border-lime/30 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
              <div className="flex items-center space-x-2">
                <span className="w-2 h-2 rounded-full bg-lime animate-pulse" />
                <span className="font-semibold text-content-primary">Today — In Progress:</span>
                <span className="text-content-muted text-[11px] font-mono">
                  {weeklySummary.today_in_progress.date} ({weeklySummary.today_in_progress.day_name})
                </span>
                <span className="text-[9px] font-mono px-1 rounded bg-amber-950/60 text-amber-400 border border-amber-400/30">
                  EXCLUDED FROM 7-DAY TOTAL
                </span>
              </div>
              <div className="flex items-center space-x-3 font-mono">
                <span className="text-content-muted text-[11px]">
                  {weeklySummary.today_in_progress.delivery_count} trips
                </span>
                <span className="font-bold text-lime">
                  {weeklySummary.today_in_progress.gross_inr} gross
                </span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Trend Area Chart */}
      <div className="bg-surface-1 border border-hairline rounded-2xl p-6 shadow-card">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-xs font-semibold tracking-tight text-content-primary">
              Income Trajectory Over Sessions
            </h3>
            <p className="text-[11px] text-content-muted">
              {viewMode === "net" ? "Net Take-Home" : "Gross Payout"} progression across historical deliveries
            </p>
          </div>
          <div className="flex items-center space-x-3 text-[11px]">
            <span className="flex items-center space-x-1.5 text-content-muted">
              <span className="w-2 h-2 rounded-full bg-lime shadow-lime-sm" />
              <span>{viewMode === "net" ? "Net Income" : "Gross"}</span>
            </span>
          </div>
        </div>

        {/* SVG Curve */}
        <div className="h-44 w-full relative pt-2 animate-graph-rise">
          <svg viewBox="0 0 600 120" preserveAspectRatio="none" className="w-full h-full">
            <defs>
              <linearGradient id="earningsGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#D7F52F" stopOpacity="0.3" />
                <stop offset="100%" stopColor="#D7F52F" stopOpacity="0.0" />
              </linearGradient>
            </defs>
            <path
              d="M0 90 Q 75 95, 150 65 T 300 45 T 450 30 T 600 15 L 600 120 L 0 120 Z"
              fill="url(#earningsGradient)"
            />
            <path
              d="M0 90 Q 75 95, 150 65 T 300 45 T 450 30 T 600 15"
              fill="none"
              stroke="#D7F52F"
              strokeWidth="2.5"
              strokeLinecap="round"
            />
          </svg>
        </div>
      </div>

      {/* Historical Deliveries & Payouts Table */}
      <div className="bg-surface-1 border border-hairline rounded-2xl overflow-hidden shadow-card">
        <div className="p-5 border-b border-hairline flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-xs text-content-primary">Delivery Operational Ledger</h3>
            <p className="text-[11px] text-content-muted">Showing {filteredDeliveries.length} recorded delivery dispatches</p>
          </div>
          <span className="text-[10px] font-mono bg-surface-2 px-2.5 py-1 rounded-full border border-hairline text-content-secondary">
            64-Bit Integer Precision
          </span>
        </div>

        <div className="overflow-x-auto max-h-96 overflow-y-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-surface-2/80 text-content-muted uppercase text-[10px] tracking-wider sticky top-0 border-b border-hairline backdrop-blur-sm">
              <tr>
                <th className="py-3 px-4 font-semibold">Completion Time</th>
                <th className="py-3 px-4 font-semibold">Platform</th>
                <th className="py-3 px-4 font-semibold">Pickup Zone</th>
                <th className="py-3 px-4 font-semibold">Distance</th>
                <th className="py-3 px-4 text-right font-semibold">Base Payout</th>
                <th className="py-3 px-4 text-right font-semibold">Incentive</th>
                <th className="py-3 px-4 text-right font-semibold">Tip</th>
                <th className="py-3 px-4 text-right font-semibold">Total (INR)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-hairline">
              {filteredDeliveries.slice(0, 30).map((d) => {
                const totalPaise = d.payout_paise + d.incentive_paise + d.tip_paise;
                const totalInr = (totalPaise / 100).toFixed(2);
                return (
                  <tr key={d.id} className="hover:bg-surface-hover/50 transition-colors">
                    <td className="py-2.5 px-4 text-content-secondary font-mono text-[11px]">
                      {new Date(d.completed_at).toLocaleString("en-IN", {
                        month: "short",
                        day: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </td>
                    <td className="py-2.5 px-4">
                      <span className="px-2 py-0.5 rounded-full bg-surface-2 border border-hairline text-[10px] font-bold text-content-primary uppercase">
                        {d.platform_code.replace("_", " ")}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-content-secondary text-[11px] font-mono">
                      {d.pickup_zone_code?.replace("zone_", "").toUpperCase() || "—"}
                    </td>
                    <td className="py-2.5 px-4 text-content-muted font-mono text-[11px]">
                      {d.distance_m ? `${(d.distance_m / 1000).toFixed(1)} km` : "—"}
                    </td>
                    <td className="py-2.5 px-4 text-right font-mono text-content-primary">
                      ₹{(d.payout_paise / 100).toFixed(2)}
                    </td>
                    <td className="py-2.5 px-4 text-right font-mono text-lime">
                      {d.incentive_paise > 0 ? `+₹${(d.incentive_paise / 100).toFixed(2)}` : "—"}
                    </td>
                    <td className="py-2.5 px-4 text-right font-mono text-content-secondary">
                      {d.tip_paise > 0 ? `+₹${(d.tip_paise / 100).toFixed(2)}` : "—"}
                    </td>
                    <td className="py-2.5 px-4 text-right font-mono font-bold text-lime">
                      ₹{totalInr}
                    </td>
                  </tr>
                );
              })}
              {filteredDeliveries.length === 0 && (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-content-muted">
                    No delivery records match the current filter.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
