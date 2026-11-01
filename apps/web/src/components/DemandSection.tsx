"use client";

import React, { useState, useEffect } from "react";
import {
  AlertCircle,
  BarChart2,
  Calendar,
  Clock,
  Info,
  MapPin,
  RefreshCw,
  TrendingUp,
  Zap,
} from "lucide-react";
import { api } from "../lib/api";
import { GlobeView } from "./GlobeView";
import { DataBadge } from "./DataBadge";

export const DemandSection: React.FC = () => {
  const [selectedZones, setSelectedZones] = useState<string[]>([
    "HYD_ZONE_01",
    "HYD_ZONE_02",
    "HYD_ZONE_05",
    "HYD_ZONE_10",
  ]);
  const [targetType, setTargetType] = useState<string>("observed_deliveries");
  const [steps, setSteps] = useState<number>(8); // 4 hours in 30-min steps
  const [forecastData, setForecastData] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchForecast = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const now = new Date();
      now.setMinutes(now.getMinutes() > 30 ? 60 : 30, 0, 0);

      const res = await api.forecastDemand({
        zone_codes: selectedZones,
        forecast_from: now.toISOString(),
        steps: steps,
        interval_minutes: 30,
        target_type: targetType,
      });

      setForecastData(res);
    } catch (err: any) {
      setError(err.message || "Failed to fetch zone demand forecast.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchForecast();
  }, [selectedZones, targetType, steps]);

  return (
    <div className="p-5 md:p-8 space-y-6 max-w-[1600px] mx-auto select-none">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-content-primary flex items-center space-x-2">
            <span>Spatio-Temporal Zone Demand Forecasting</span>
          </h2>
          <p className="text-xs text-content-muted mt-0.5">
            Multi-horizon recursive gradient boosted trees predicting order volumes per 30-minute interval with uncertainty bounds
          </p>
        </div>

        <button
          onClick={fetchForecast}
          disabled={isLoading}
          className="flex items-center space-x-2 px-4 py-2 rounded-full bg-surface-1 border border-hairline hover:border-lime/40 text-xs font-semibold text-content-primary hover:text-lime transition-all self-start sm:self-auto shadow-card"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin text-lime" : ""}`} />
          <span>Refresh Forecast</span>
        </button>
      </div>

      {/* Target Integrity Note */}
      <div className="bg-surface-1 border border-hairline rounded-2xl p-4 flex items-start space-x-3 text-xs shadow-card">
        <Info className="w-4 h-4 text-lime shrink-0 mt-0.5" />
        <p className="text-content-secondary leading-relaxed text-[11px]">
          <strong className="text-content-primary">Target Integrity Guarantee:</strong> Observed completed deliveries are strictly separated from raw market demand. The current target classification is:{" "}
          <span className="font-mono text-lime bg-surface-2 px-2 py-0.5 rounded-full border border-hairline font-bold">
            {targetType}
          </span>
          .
        </p>
      </div>

      {/* Controls Strip */}
      <div className="bg-surface-1 border border-hairline rounded-2xl p-5 grid grid-cols-1 sm:grid-cols-3 gap-5 shadow-card">
        <div>
          <label className="text-[11px] font-semibold text-content-muted block mb-1.5 uppercase tracking-wider">
            Target Classification
          </label>
          <select
            value={targetType}
            onChange={(e) => setTargetType(e.target.value)}
            className="w-full bg-surface-2 border border-hairline rounded-xl px-3 py-2 text-xs text-content-primary focus:outline-none focus:border-lime cursor-pointer"
          >
            <option value="observed_deliveries" className="bg-surface-1">Observed Deliveries (Verified)</option>
            <option value="completed_orders" className="bg-surface-1">Completed Orders (Sample)</option>
            <option value="requested_orders" className="bg-surface-1">Requested Orders (Market)</option>
            <option value="proxy" className="bg-surface-1">Activity Index (Proxy)</option>
          </select>
        </div>

        <div>
          <label className="text-[11px] font-semibold text-content-muted block mb-1.5 uppercase tracking-wider">
            Horizon Steps (30-min each)
          </label>
          <select
            value={steps}
            onChange={(e) => setSteps(Number(e.target.value))}
            className="w-full bg-surface-2 border border-hairline rounded-xl px-3 py-2 text-xs text-content-primary focus:outline-none focus:border-lime font-mono cursor-pointer"
          >
            <option value={4} className="bg-surface-1">4 Steps (2 Hours)</option>
            <option value={8} className="bg-surface-1">8 Steps (4 Hours)</option>
            <option value={12} className="bg-surface-1">12 Steps (6 Hours)</option>
            <option value={16} className="bg-surface-1">16 Steps (8 Hours)</option>
          </select>
        </div>

        <div>
          <label className="text-[11px] font-semibold text-content-muted block mb-1.5 uppercase tracking-wider">
            Active Study Zones
          </label>
          <div className="flex flex-wrap gap-1.5 mt-1">
            {["HYD_ZONE_01", "HYD_ZONE_02", "HYD_ZONE_05", "HYD_ZONE_10", "HYD_ZONE_13"].map((z) => {
              const active = selectedZones.includes(z);
              return (
                <button
                  key={z}
                  onClick={() => {
                    if (active && selectedZones.length > 1) {
                      setSelectedZones(selectedZones.filter((x) => x !== z));
                    } else if (!active) {
                      setSelectedZones([...selectedZones, z]);
                    }
                  }}
                  className={`px-2.5 py-1 rounded-full text-[10px] font-mono transition-all ${
                    active
                      ? "bg-lime text-canvas font-bold shadow-lime-sm"
                      : "bg-surface-2 text-content-muted hover:text-content-primary border border-hairline"
                  }`}
                >
                  {z}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-semantic-red/10 border border-semantic-red/30 rounded-2xl text-xs text-semantic-red flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* 3D Spatial Globe Projection & Live Clusters */}
      <GlobeView className="shadow-card min-h-[420px]" />

      {/* Multi-Zone Demand Forecast Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        {selectedZones.map((zone) => {
          const zoneSteps = forecastData?.forecasts?.filter((f: any) => f.zone_code === zone) || [];
          const avgDemand = zoneSteps.length > 0
            ? (zoneSteps.reduce((acc: number, curr: any) => acc + curr.point_prediction, 0) / zoneSteps.length).toFixed(1)
            : "—";

          const peakStep = zoneSteps.length > 0
            ? [...zoneSteps].sort((a, b) => b.point_prediction - a.point_prediction)[0]
            : null;

          return (
            <div key={zone} className="bg-surface-1 border border-hairline rounded-2xl p-5 space-y-4 shadow-card hover:border-hairline-strong transition-all">
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-bold text-sm text-content-primary font-mono">{zone}</h4>
                  <span className="text-[10px] text-content-muted">Spatial Study Cluster</span>
                </div>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] bg-lime-muted text-lime font-bold border border-lime/30 font-mono">
                  Avg: {avgDemand}/30m
                </span>
              </div>

              {/* Step Forecast Mini Bars */}
              <div className="space-y-2 pt-1">
                <span className="text-[10px] text-content-muted uppercase tracking-wider block font-semibold">
                  Forecast Timeline (30-min horizon)
                </span>
                <div className="space-y-1.5">
                  {zoneSteps.slice(0, 6).map((s: any) => {
                    const timeLabel = new Date(s.interval_start).toLocaleTimeString("en-IN", {
                      hour: "2-digit",
                      minute: "2-digit",
                    });
                    const maxScale = 30;
                    const barPct = Math.min(100, (s.point_prediction / maxScale) * 100);

                    return (
                      <div key={s.interval_start} className="text-xs space-y-1">
                        <div className="flex justify-between text-[11px]">
                          <span className="text-content-muted font-mono">{timeLabel}</span>
                          <span className="font-mono text-content-primary">
                            <strong className="text-lime">{s.point_prediction}</strong>{" "}
                            <span className="text-[10px] text-content-muted font-normal">
                              [{s.lower_prediction}–{s.upper_prediction}]
                            </span>
                          </span>
                        </div>
                        <div className="w-full bg-surface-2 h-1.5 rounded-full overflow-hidden border border-hairline/40">
                          <div
                            className="bg-lime h-full rounded-full transition-all duration-500 shadow-lime-sm"
                            style={{ width: `${barPct}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {peakStep && (
                <div className="border-t border-hairline pt-3 text-[10px] text-content-muted flex justify-between">
                  <span>Peak Demand Window:</span>
                  <span className="font-semibold text-lime font-mono">
                    {new Date(peakStep.interval_start).toLocaleTimeString("en-IN", {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}{" "}
                    ({peakStep.point_prediction} orders)
                  </span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
