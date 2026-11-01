"use client";

import React, { useState } from "react";
import { Activity, Clock, Filter, MapPin, Search } from "lucide-react";

interface DeliveriesSectionProps {
  deliveries: any[];
}

export const DeliveriesSection: React.FC<DeliveriesSectionProps> = ({ deliveries }) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  const filtered = deliveries.filter((d) => {
    const matchesSearch =
      d.platform_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (d.pickup_zone_code && d.pickup_zone_code.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (d.drop_zone_code && d.drop_zone_code.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesStatus = statusFilter === "all" ? true : d.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="p-5 md:p-8 space-y-6 max-w-[1600px] mx-auto select-none">
      <div>
        <h2 className="text-xl font-bold tracking-tight text-content-primary flex items-center space-x-2">
          <span>Delivery Activity & Dispatch Log</span>
        </h2>
        <p className="text-xs text-content-muted mt-0.5">
          Recorded dispatches, transit distances, durations, and exact payouts in 64-bit integer paise
        </p>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-surface-1 border border-hairline rounded-2xl p-4 flex flex-col sm:flex-row gap-3 justify-between items-center shadow-card">
        <div className="relative w-full sm:w-80">
          <Search className="w-3.5 h-3.5 text-content-muted absolute left-3.5 top-3" />
          <input
            type="text"
            placeholder="Filter platform or zone..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-surface-2 border border-hairline rounded-full pl-9 pr-4 py-2 text-xs text-content-primary focus:outline-none focus:border-lime"
          />
        </div>

        <div className="flex items-center space-x-3 w-full sm:w-auto">
          <div className="flex items-center space-x-2 bg-surface-2 border border-hairline px-3 py-1.5 rounded-full text-xs text-content-secondary">
            <span className="text-content-muted text-[10px] uppercase font-semibold">Status:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-transparent text-content-primary focus:outline-none cursor-pointer"
            >
              <option value="all" className="bg-surface-1">All Dispatches</option>
              <option value="completed" className="bg-surface-1">Completed</option>
              <option value="cancelled" className="bg-surface-1">Cancelled</option>
            </select>
          </div>
          <span className="text-[11px] text-content-muted font-mono">{filtered.length} records</span>
        </div>
      </div>

      {/* Deliveries Table */}
      <div className="bg-surface-1 border border-hairline rounded-2xl overflow-hidden shadow-card">
        <div className="overflow-x-auto max-h-[550px] overflow-y-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-surface-2/80 text-content-muted uppercase text-[10px] tracking-wider sticky top-0 border-b border-hairline backdrop-blur-sm">
              <tr>
                <th className="py-3 px-4 font-semibold">Completion Date</th>
                <th className="py-3 px-4 font-semibold">Platform</th>
                <th className="py-3 px-4 font-semibold">Pickup → Drop Zone</th>
                <th className="py-3 px-4 font-semibold">Distance</th>
                <th className="py-3 px-4 font-semibold">Duration</th>
                <th className="py-3 px-4 text-right font-semibold">Base Payout</th>
                <th className="py-3 px-4 text-right font-semibold">Incentive</th>
                <th className="py-3 px-4 text-right font-semibold">Tip</th>
                <th className="py-3 px-4 text-right font-semibold">Total Payout</th>
                <th className="py-3 px-4 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-hairline">
              {filtered.map((d) => {
                const totalPaise = d.payout_paise + d.incentive_paise + d.tip_paise;
                const durMin = d.duration_seconds ? Math.round(d.duration_seconds / 60) : "—";

                return (
                  <tr key={d.id} className="hover:bg-surface-hover/50 transition-colors">
                    <td className="py-2.5 px-4 text-content-secondary font-mono text-[11px] whitespace-nowrap">
                      {new Date(d.completed_at).toLocaleString("en-IN", {
                        month: "short",
                        day: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </td>
                    <td className="py-2.5 px-4 whitespace-nowrap">
                      <span className="px-2 py-0.5 rounded-full bg-surface-2 border border-hairline text-[10px] font-bold text-content-primary uppercase">
                        {d.platform_code.replace("_", " ")}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-content-secondary whitespace-nowrap text-[11px]">
                      <span className="text-content-primary font-mono">{d.pickup_zone_code?.replace("zone_", "").toUpperCase() || "—"}</span>
                      {d.drop_zone_code && (
                        <span className="text-content-muted font-mono"> → {d.drop_zone_code.replace("zone_", "").toUpperCase()}</span>
                      )}
                    </td>
                    <td className="py-2.5 px-4 text-content-muted font-mono whitespace-nowrap text-[11px]">
                      {d.distance_m ? `${(d.distance_m / 1000).toFixed(1)} km` : "—"}
                    </td>
                    <td className="py-2.5 px-4 text-content-muted font-mono whitespace-nowrap text-[11px]">
                      {durMin !== "—" ? `${durMin} min` : "—"}
                    </td>
                    <td className="py-2.5 px-4 text-right font-mono text-content-primary whitespace-nowrap">
                      ₹{(d.payout_paise / 100).toFixed(2)}
                    </td>
                    <td className="py-2.5 px-4 text-right font-mono text-lime whitespace-nowrap">
                      {d.incentive_paise > 0 ? `+₹${(d.incentive_paise / 100).toFixed(2)}` : "—"}
                    </td>
                    <td className="py-2.5 px-4 text-right font-mono text-content-secondary whitespace-nowrap">
                      {d.tip_paise > 0 ? `+₹${(d.tip_paise / 100).toFixed(2)}` : "—"}
                    </td>
                    <td className="py-2.5 px-4 text-right font-mono font-bold text-lime whitespace-nowrap">
                      ₹{(totalPaise / 100).toFixed(2)}
                    </td>
                    <td className="py-2.5 px-4 whitespace-nowrap">
                      <span
                        className={`px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider ${
                          d.status === "completed"
                            ? "bg-lime-muted text-lime border border-lime/30"
                            : "bg-semantic-red/10 text-semantic-red border border-semantic-red/30"
                        }`}
                      >
                        {d.status}
                      </span>
                    </td>
                  </tr>
                );
              })}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={10} className="py-12 text-center text-content-muted">
                    No delivery records match current criteria.
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
