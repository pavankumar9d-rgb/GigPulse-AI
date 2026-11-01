"use client";

import React, { useState } from "react";
import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Compass,
  Filter,
  Fuel,
  Info,
  MapPin,
  RefreshCw,
  ShieldAlert,
  Sliders,
  TrendingUp,
  Zap,
} from "lucide-react";
import { api } from "../lib/api";

interface RecommendationsProps {
  workerRef: string;
}

export const RecommendationsSection: React.FC<RecommendationsProps> = ({ workerRef }) => {
  const [minRateInr, setMinRateInr] = useState<number>(100);
  const [maxDistanceKm, setMaxDistanceKm] = useState<number>(15);
  const [riskTolerance, setRiskTolerance] = useState<string>("balanced");
  const [currentZone, setCurrentZone] = useState<string>("zone_koramangala");
  const [results, setResults] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const now = new Date();
      now.setHours(18, 0, 0, 0); // Evening peak 6 PM
      const startAt = new Date(now.getTime() + 24 * 3600 * 1000);
      const endAt = new Date(startAt.getTime() + 4 * 3600 * 1000); // 4-hour shift

      const res = await api.getRecommendations({
        worker_ref: workerRef,
        candidate_platform_ids: ["flash_drop", "swift_bite", "hyper_courier"],
        candidate_zone_ids: [
          "zone_koramangala",
          "zone_indiranagar",
          "zone_hsr",
          "zone_whitefield",
          "zone_jayanagar",
        ],
        time_window: {
          start_at: startAt.toISOString(),
          end_at: endAt.toISOString(),
        },
        preferences: {
          min_net_earnings_paise_per_hour: minRateInr * 100,
          max_travel_distance_m: maxDistanceKm * 1000,
          risk_tolerance: riskTolerance,
          current_zone_code: currentZone,
          exclude_platform_ids: [],
          exclude_zone_ids: [],
        },
      });

      setResults(res);
    } catch (err: any) {
      setError(err.message || "Failed to generate recommendations.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-5 md:p-8 space-y-6 max-w-[1600px] mx-auto select-none">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold tracking-tight text-content-primary flex items-center space-x-2">
          <span>Opportunity Planner & Intelligent Decision Support</span>
        </h2>
        <p className="text-xs text-content-muted mt-0.5">
          Multi-objective optimizer: Score = Net Rate − Uncertainty Penalty − Fuel Travel Cost. Enforces hard worker constraints with transparent reasoning.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Preference Controls Card */}
        <div className="lg:col-span-4 bg-surface-1 border border-hairline rounded-2xl p-6 space-y-5 shadow-card">
          <div className="flex items-center justify-between border-b border-hairline/60 pb-3">
            <h3 className="text-xs font-semibold text-content-primary uppercase tracking-wider">
              Shift Constraints
            </h3>
            <span className="text-[10px] font-mono text-lime bg-lime-muted px-2 py-0.5 rounded-full border border-lime/30">
              Pareto Filter
            </span>
          </div>

          <div className="space-y-4">
            <div>
              <label className="text-[11px] font-medium text-content-muted block mb-1.5">
                Current Departure Zone
              </label>
              <select
                value={currentZone}
                onChange={(e) => setCurrentZone(e.target.value)}
                className="w-full bg-surface-2 border border-hairline rounded-xl px-3.5 py-2.5 text-xs text-content-primary focus:outline-none focus:border-lime cursor-pointer"
              >
                <option value="zone_koramangala" className="bg-surface-1">Koramangala</option>
                <option value="zone_indiranagar" className="bg-surface-1">Indiranagar</option>
                <option value="zone_hsr" className="bg-surface-1">HSR Layout</option>
                <option value="zone_whitefield" className="bg-surface-1">Whitefield</option>
                <option value="zone_jayanagar" className="bg-surface-1">Jayanagar</option>
              </select>
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1.5">
                <span className="text-content-muted">Max Transit Radius</span>
                <span className="font-mono text-lime font-bold">{maxDistanceKm} km</span>
              </div>
              <input
                type="range"
                min={3}
                max={25}
                value={maxDistanceKm}
                onChange={(e) => setMaxDistanceKm(Number(e.target.value))}
                className="w-full accent-lime cursor-pointer bg-surface-2 h-1.5 rounded-full"
              />
              <span className="text-[10px] text-content-muted mt-1 block">
                Excludes far-off zones that burn transit fuel
              </span>
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1.5">
                <span className="text-content-muted">Min Net Hourly Wage</span>
                <span className="font-mono text-lime font-bold">₹{minRateInr}/hr</span>
              </div>
              <input
                type="range"
                min={50}
                max={250}
                step={10}
                value={minRateInr}
                onChange={(e) => setMinRateInr(Number(e.target.value))}
                className="w-full accent-lime cursor-pointer bg-surface-2 h-1.5 rounded-full"
              />
              <span className="text-[10px] text-content-muted mt-1 block">
                Hard threshold filtering out low-margin shifts
              </span>
            </div>

            <div>
              <label className="text-[11px] font-medium text-content-muted block mb-1.5">
                Uncertainty Risk Mode
              </label>
              <div className="grid grid-cols-3 gap-1.5 bg-surface-2 p-1.5 rounded-xl border border-hairline text-xs">
                {["risk_averse", "balanced", "risk_tolerant"].map((mode) => (
                  <button
                    key={mode}
                    onClick={() => setRiskTolerance(mode)}
                    className={`py-1.5 rounded-lg font-medium capitalize text-[10px] transition-all ${
                      riskTolerance === mode
                        ? "bg-lime text-canvas font-bold shadow-lime-sm"
                        : "text-content-muted hover:text-content-primary"
                    }`}
                  >
                    {mode.replace("_", " ")}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <button
            onClick={handleGenerate}
            disabled={isLoading}
            className="w-full py-3 bg-lime hover:bg-lime-bright text-canvas font-bold rounded-full text-xs uppercase tracking-wider transition-all shadow-lime-glow disabled:opacity-50 flex items-center justify-center space-x-2"
          >
            {isLoading ? (
              <span>Evaluating Candidate Matrix...</span>
            ) : (
              <>
                <Compass className="w-4 h-4 stroke-[2.5]" />
                <span>Evaluate Optimal Opportunities</span>
              </>
            )}
          </button>

          {error && (
            <div className="p-3 bg-semantic-red/10 border border-semantic-red/30 rounded-xl text-xs text-semantic-red">
              {error}
            </div>
          )}
        </div>

        {/* Ranked Recommendations List */}
        <div className="lg:col-span-8 space-y-4">
          {results ? (
            <>
              <div className="flex items-center justify-between text-xs text-content-muted px-1">
                <span>
                  Evaluated <strong>{results.total_evaluated}</strong> candidates ({results.viable_count} viable options,{" "}
                  {results.excluded_candidates.length} filtered by hard constraints)
                </span>
                <span className="font-mono text-lime bg-lime-muted px-2 py-0.5 rounded-full border border-lime/20 text-[10px]">
                  Scoring Engine {results.scoring_version}
                </span>
              </div>

              {/* Candidates Cards */}
              <div className="space-y-4">
                {results.ranked_candidates.slice(0, 5).map((cand: any, idx: number) => {
                  const isTop = idx === 0;
                  return (
                    <div
                      key={cand.candidate_id}
                      className={`p-5 rounded-2xl border transition-all shadow-card relative overflow-hidden ${
                        isTop
                          ? "bg-surface-1 border-lime/50 shadow-lime-glow"
                          : "bg-surface-1 border-hairline hover:border-hairline-strong"
                      }`}
                    >
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-hairline gap-3">
                        <div className="flex items-center space-x-2.5">
                          {isTop && (
                            <span className="px-2.5 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider bg-lime text-canvas shadow-lime-sm">
                              #1 Optimal Pick
                            </span>
                          )}
                          <h4 className="font-bold text-sm text-content-primary uppercase tracking-wide">
                            {cand.platform_code.replace("_", " ")}
                          </h4>
                          <span className="text-content-muted">•</span>
                          <span className="text-xs text-content-secondary flex items-center space-x-1 font-mono">
                            <MapPin className="w-3.5 h-3.5 text-lime" />
                            <span>{cand.zone_code.replace("zone_", "").toUpperCase()}</span>
                          </span>
                        </div>

                        <div className="flex items-center space-x-4 text-right">
                          <div>
                            <span className="text-[10px] text-content-muted block uppercase font-semibold">Net Rate</span>
                            <span className="text-lg font-bold font-mono text-lime">
                              ₹{cand.expected_net_inr_per_hour}/hr
                            </span>
                          </div>
                          <div className="border-l border-hairline pl-4">
                            <span className="text-[10px] text-content-muted block uppercase font-semibold">Score</span>
                            <span className="text-lg font-bold font-mono text-content-primary">
                              {cand.composite_score}
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Financial & Transit Snapshot */}
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 text-xs">
                        <div>
                          <span className="text-[10px] text-content-muted block uppercase">Session Gross</span>
                          <span className="font-mono text-content-primary font-semibold">{cand.expected_session_gross_inr}</span>
                        </div>
                        <div>
                          <span className="text-[10px] text-content-muted block uppercase">Transit Radius</span>
                          <span className="font-mono text-content-primary">{(cand.travel_distance_m / 1000).toFixed(1)} km</span>
                        </div>
                        <div>
                          <span className="text-[10px] text-content-muted block uppercase">Transit Fuel Cost</span>
                          <span className="font-mono text-semantic-red font-semibold">₹{cand.travel_cost_inr}</span>
                        </div>
                        <div>
                          <span className="text-[10px] text-content-muted block uppercase">Confidence Range</span>
                          <span className="font-mono text-content-secondary">
                            ₹{cand.q10_inr_per_hour}–₹{cand.q90_inr_per_hour}
                          </span>
                        </div>
                      </div>

                      {/* Explainability Bullets */}
                      <div className="mt-3.5 bg-surface-2/60 p-3 rounded-xl border border-hairline space-y-1">
                        <span className="text-[10px] uppercase font-bold text-content-muted tracking-wider block">
                          Recommendation Rationale:
                        </span>
                        <ul className="text-[11px] text-content-secondary space-y-0.5 list-disc list-inside">
                          {cand.reasons.map((r: string, rIdx: number) => (
                            <li key={rIdx}>{r}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Excluded Candidates Drawer */}
              {results.excluded_candidates.length > 0 && (
                <div className="bg-surface-1 border border-hairline rounded-2xl p-5 space-y-2.5 shadow-card">
                  <h4 className="text-xs font-semibold text-content-muted flex items-center space-x-2">
                    <Filter className="w-3.5 h-3.5" />
                    <span>Hard Constraint Exclusions ({results.excluded_candidates.length})</span>
                  </h4>
                  <div className="space-y-1.5 max-h-36 overflow-y-auto pr-1">
                    {results.excluded_candidates.map((e: any) => (
                      <div key={e.candidate_id} className="text-[11px] text-content-muted flex justify-between py-1 border-b border-hairline">
                        <span className="font-mono text-content-primary uppercase">
                          {e.platform_code} — {e.zone_code.replace("zone_", "")}
                        </span>
                        <span className="text-semantic-red text-[10px]">{e.reason}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Advisory Disclaimer */}
              <div className="text-[11px] text-content-muted bg-surface-1 p-3.5 rounded-2xl border border-hairline flex items-start space-x-2.5">
                <ShieldAlert className="w-4 h-4 text-lime shrink-0 mt-0.5" />
                <p className="leading-relaxed">{results.disclaimer}</p>
              </div>
            </>
          ) : (
            <div className="bg-surface-1 border border-hairline rounded-2xl p-16 text-center space-y-4 shadow-card">
              <div className="w-14 h-14 rounded-full bg-surface-2 border border-hairline flex items-center justify-center mx-auto text-lime">
                <Compass className="w-7 h-7" />
              </div>
              <h3 className="text-sm font-semibold text-content-primary">Opportunity Planner Ready</h3>
              <p className="text-xs text-content-muted max-w-md mx-auto leading-relaxed">
                Adjust departure zone, travel distance limit, and wage thresholds on the left to evaluate all multi-platform candidate shifts.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
