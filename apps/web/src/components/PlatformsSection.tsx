"use client";

import React from "react";
import { BarChart3, CheckCircle, IndianRupee, PieChart, TrendingUp, Zap } from "lucide-react";

interface PlatformsProps {
  summary: any;
  deliveries: any[];
}

export const PlatformsSection: React.FC<PlatformsProps> = ({ summary, deliveries }) => {
  const analytics = summary?.analytics;
  const platformShares = analytics?.platform_gross_shares || {};

  // Compute platform-wise statistics
  const platformStats: Record<
    string,
    { count: number; grossPaise: number; avgPayoutPaise: number; tipsCount: number; maxPayoutPaise: number }
  > = {};

  deliveries.forEach((d) => {
    const p = d.platform_code;
    if (!platformStats[p]) {
      platformStats[p] = { count: 0, grossPaise: 0, avgPayoutPaise: 0, tipsCount: 0, maxPayoutPaise: 0 };
    }
    const tot = d.payout_paise + d.incentive_paise + d.tip_paise;
    platformStats[p].count += 1;
    platformStats[p].grossPaise += tot;
    if (d.tip_paise > 0) platformStats[p].tipsCount += 1;
    if (tot > platformStats[p].maxPayoutPaise) platformStats[p].maxPayoutPaise = tot;
  });

  Object.keys(platformStats).forEach((p) => {
    if (platformStats[p].count > 0) {
      platformStats[p].avgPayoutPaise = Math.round(platformStats[p].grossPaise / platformStats[p].count);
    }
  });

  return (
    <div className="p-5 md:p-8 space-y-6 max-w-[1600px] mx-auto select-none">
      <div>
        <h2 className="text-xl font-bold tracking-tight text-content-primary flex items-center space-x-2">
          <span>Multi-Platform Comparison & Multi-Homing Insights</span>
        </h2>
        <p className="text-xs text-content-muted mt-0.5">
          Side-by-side performance benchmarks across delivery aggregators to evaluate compensation rates
        </p>
      </div>

      {/* Platform Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {Object.entries(platformStats).map(([platCode, stats]) => {
          const sharePct = ((platformShares[platCode] || 0) * 100).toFixed(1);
          const tipPct = stats.count > 0 ? ((stats.tipsCount / stats.count) * 100).toFixed(0) : "0";

          return (
            <div
              key={platCode}
              className="bg-surface-1 border border-hairline rounded-2xl p-6 space-y-5 shadow-card hover:border-hairline-strong transition-all relative overflow-hidden"
            >
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-bold text-base text-content-primary uppercase tracking-wide">
                    {platCode.replace("_", " ")}
                  </h3>
                  <span className="text-[11px] text-lime font-medium flex items-center space-x-1 mt-0.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-lime shadow-lime-sm" />
                    <span>Active Integration</span>
                  </span>
                </div>
                <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-lime-muted text-lime border border-lime/30">
                  {sharePct}% Share
                </span>
              </div>

              {/* Quick Metrics */}
              <div className="grid grid-cols-2 gap-3 pt-1">
                <div className="bg-surface-2/60 p-3 rounded-xl border border-hairline">
                  <span className="text-[10px] text-content-muted block uppercase font-semibold">Completed Trips</span>
                  <span className="text-xl font-bold font-mono text-content-primary mt-0.5 block">{stats.count}</span>
                </div>
                <div className="bg-surface-2/60 p-3 rounded-xl border border-hairline">
                  <span className="text-[10px] text-content-muted block uppercase font-semibold">Gross Revenue</span>
                  <span className="text-xl font-bold font-mono text-lime mt-0.5 block">
                    ₹{(stats.grossPaise / 100).toLocaleString("en-IN", { maximumFractionDigits: 0 })}
                  </span>
                </div>
              </div>

              {/* Secondary Details */}
              <div className="space-y-2.5 text-xs border-t border-hairline pt-4">
                <div className="flex justify-between text-content-muted">
                  <span>Avg Payout / Delivery:</span>
                  <span className="font-mono text-content-primary font-semibold">
                    ₹{(stats.avgPayoutPaise / 100).toFixed(2)}
                  </span>
                </div>
                <div className="flex justify-between text-content-muted">
                  <span>Customer Tip Rate:</span>
                  <span className="font-mono text-content-secondary font-semibold">
                    {tipPct}% of orders
                  </span>
                </div>
                <div className="flex justify-between text-content-muted">
                  <span>Max Peak Payout:</span>
                  <span className="font-mono text-lime font-semibold">
                    ₹{(stats.maxPayoutPaise / 100).toFixed(2)}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
