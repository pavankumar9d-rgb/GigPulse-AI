"use client";

import React, { useState } from "react";
import {
  Calendar,
  Clock,
  Compass,
  HelpCircle,
  IndianRupee,
  Layers,
  MapPin,
  ShieldAlert,
  Sparkles,
  Zap,
} from "lucide-react";
import { api } from "../lib/api";

interface PredictionProps {
  workerRef: string;
}

export const PredictionSection: React.FC<PredictionProps> = ({ workerRef }) => {
  const [platform, setPlatform] = useState<string>("flash_drop");
  const [zone, setZone] = useState<string>("zone_koramangala");
  const [durationHours, setDurationHours] = useState<number>(4);
  const [startHour, setStartHour] = useState<number>(18); // 6 PM peak
  const [prediction, setPrediction] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handlePredict = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const now = new Date();
      now.setHours(startHour, 0, 0, 0);
      const startAt = new Date(now.getTime() + 24 * 3600 * 1000); // tomorrow
      const endAt = new Date(startAt.getTime() + durationHours * 3600 * 1000);

      const res = await api.predictEarnings({
        worker_ref: workerRef,
        platform_code: platform,
        zone_code: zone,
        start_at: startAt.toISOString(),
        end_at: endAt.toISOString(),
        prediction_unit: "INR_PER_ONLINE_HOUR",
        include_interval: true,
      });

      setPrediction(res);
    } catch (err: any) {
      setError(err.message || "Failed to generate prediction.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-5 md:p-8 space-y-6 max-w-[1600px] mx-auto select-none">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold tracking-tight text-content-primary flex items-center space-x-2">
          <span>Machine Learning Earnings Predictor</span>
        </h2>
        <p className="text-xs text-content-muted mt-0.5">
          Trained gradient boosted regression with Q10–Q50–Q90 quantile loss estimating take-home rate per online hour
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Input Parameters Card */}
        <div className="lg:col-span-4 bg-surface-1 border border-hairline rounded-2xl p-6 space-y-5 shadow-card">
          <div className="flex items-center justify-between border-b border-hairline/60 pb-3">
            <h3 className="text-xs font-semibold text-content-primary uppercase tracking-wider">
              Shift Parameters
            </h3>
            <span className="text-[10px] font-mono text-lime bg-lime-muted px-2 py-0.5 rounded-full border border-lime/30">
              Point-in-Time
            </span>
          </div>

          <div className="space-y-4">
            <div>
              <label className="text-[11px] font-medium text-content-muted block mb-1.5">
                Target Platform
              </label>
              <select
                value={platform}
                onChange={(e) => setPlatform(e.target.value)}
                className="w-full bg-surface-2 border border-hairline rounded-xl px-3.5 py-2.5 text-xs text-content-primary focus:outline-none focus:border-lime uppercase cursor-pointer"
              >
                <option value="flash_drop" className="bg-surface-1">FlashDrop (Courier)</option>
                <option value="swift_bite" className="bg-surface-1">SwiftBite (Food)</option>
                <option value="hyper_courier" className="bg-surface-1">HyperCourier (Express)</option>
              </select>
            </div>

            <div>
              <label className="text-[11px] font-medium text-content-muted block mb-1.5">
                Operating Zone
              </label>
              <select
                value={zone}
                onChange={(e) => setZone(e.target.value)}
                className="w-full bg-surface-2 border border-hairline rounded-xl px-3.5 py-2.5 text-xs text-content-primary focus:outline-none focus:border-lime cursor-pointer"
              >
                <option value="zone_koramangala" className="bg-surface-1">Koramangala Commercial Hub</option>
                <option value="zone_indiranagar" className="bg-surface-1">Indiranagar 100ft Road</option>
                <option value="zone_hsr" className="bg-surface-1">HSR Sector 1–7</option>
                <option value="zone_whitefield" className="bg-surface-1">Whitefield IT Corridor</option>
                <option value="zone_jayanagar" className="bg-surface-1">Jayanagar Shopping Belt</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-[11px] font-medium text-content-muted block mb-1.5">
                  Shift Start Time
                </label>
                <select
                  value={startHour}
                  onChange={(e) => setStartHour(Number(e.target.value))}
                  className="w-full bg-surface-2 border border-hairline rounded-xl px-3 py-2.5 text-xs text-content-primary focus:outline-none focus:border-lime font-mono cursor-pointer"
                >
                  <option value={7} className="bg-surface-1">07:00 (Breakfast)</option>
                  <option value={12} className="bg-surface-1">12:00 (Lunch)</option>
                  <option value={15} className="bg-surface-1">15:00 (Afternoon)</option>
                  <option value={18} className="bg-surface-1">18:00 (Dinner Peak)</option>
                  <option value={21} className="bg-surface-1">21:00 (Late Night)</option>
                </select>
              </div>

              <div>
                <label className="text-[11px] font-medium text-content-muted block mb-1.5">
                  Duration (Hours)
                </label>
                <input
                  type="number"
                  min={1}
                  max={12}
                  value={durationHours}
                  onChange={(e) => setDurationHours(Number(e.target.value))}
                  className="w-full bg-surface-2 border border-hairline rounded-xl px-3 py-2.5 text-xs text-content-primary focus:outline-none focus:border-lime font-mono"
                />
              </div>
            </div>
          </div>

          <button
            onClick={handlePredict}
            disabled={isLoading}
            className="w-full py-3 bg-lime hover:bg-lime-bright text-canvas font-bold rounded-full text-xs uppercase tracking-wider transition-all shadow-lime-glow disabled:opacity-50 flex items-center justify-center space-x-2"
          >
            {isLoading ? (
              <span>Computing Quantile Tree Inference...</span>
            ) : (
              <>
                <Zap className="w-4 h-4 stroke-[2.5]" />
                <span>Compute Earnings Forecast</span>
              </>
            )}
          </button>

          {error && (
            <div className="p-3 bg-semantic-red/10 border border-semantic-red/30 rounded-xl text-xs text-semantic-red">
              {error}
            </div>
          )}

          <div className="border-t border-hairline/60 pt-3 text-[11px] text-content-muted space-y-1">
            <span className="font-semibold text-content-primary block text-[10px] uppercase tracking-wider">
              No Data Leakage Guarantee
            </span>
            <p className="text-[10px] leading-relaxed">
              Features are strictly restricted to state available prior to shift dispatch: lag order densities, platform base rate, and time harmonic cyclical encodings.
            </p>
          </div>
        </div>

        {/* Prediction Results Display */}
        <div className="lg:col-span-8 space-y-6">
          {prediction ? (
            <div className="bg-surface-1 border border-hairline rounded-2xl p-6 space-y-6 shadow-card relative overflow-hidden">
              <div className="absolute top-0 right-0 w-48 h-48 bg-lime/5 rounded-full blur-3xl pointer-events-none" />

              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-hairline gap-3">
                <div>
                  <span className="bg-lime-muted text-lime border border-lime/30 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider">
                    Model Version: HistGBT Quantile v1.0.0
                  </span>
                  <h3 className="text-2xl font-bold font-mono text-content-primary mt-2">
                    Expected Net Rate: <span className="text-lime">₹{prediction.q50_inr_per_hour}/hr</span>
                  </h3>
                </div>
                <div className="text-right text-xs text-content-muted font-mono">
                  <span>Shift: {prediction.duration_hours}h on </span>
                  <strong className="text-content-primary uppercase">{prediction.platform_code}</strong>
                </div>
              </div>

              {/* Quantile Intervals Banner */}
              <div className="bg-surface-2/60 border border-hairline rounded-2xl p-5 space-y-4">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-semibold text-content-primary">80% Uncertainty Envelope</span>
                  <span className="text-content-muted font-mono text-[11px]">Q10 — Q50 (Median) — Q90</span>
                </div>

                {/* Range Bar */}
                <div className="space-y-2">
                  <div className="flex justify-between text-xs font-mono">
                    <span className="text-content-muted">Downside Q10: ₹{prediction.q10_inr_per_hour}/hr</span>
                    <span className="text-lime font-bold">Median Q50: ₹{prediction.q50_inr_per_hour}/hr</span>
                    <span className="text-content-secondary">Upside Q90: ₹{prediction.q90_inr_per_hour}/hr</span>
                  </div>
                  <div className="w-full bg-canvas h-4 rounded-full overflow-hidden border border-hairline relative">
                    <div
                      className="absolute top-0 bottom-0 bg-lime/20 border-l border-r border-lime/60 rounded-full"
                      style={{
                        left: `${Math.min(85, (prediction.q10_inr_per_hour / 400) * 100)}%`,
                        width: `${Math.max(12, ((prediction.q90_inr_per_hour - prediction.q10_inr_per_hour) / 400) * 100)}%`,
                      }}
                    />
                    <div
                      className="absolute top-0 bottom-0 w-2 bg-lime shadow-lime-sm rounded-full"
                      style={{
                        left: `${Math.min(95, (prediction.q50_inr_per_hour / 400) * 100)}%`,
                      }}
                    />
                  </div>
                </div>
                <p className="text-[11px] text-content-muted">
                  Under identical temporal conditions, 80% of test sessions fell within this confidence envelope.
                </p>
              </div>

              {/* Total Shift Projections */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="bg-surface-2/50 p-4 rounded-xl border border-hairline">
                  <span className="text-[10px] text-content-muted uppercase tracking-wider block font-semibold">
                    Expected Gross Payout
                  </span>
                  <span className="text-2xl font-bold font-mono text-content-primary mt-1 block">
                    {prediction.expected_gross_inr}
                  </span>
                  <span className="text-[10px] text-content-muted">Delivery fees + incentives</span>
                </div>

                <div className="bg-surface-2/50 p-4 rounded-xl border border-hairline">
                  <span className="text-[10px] text-content-muted uppercase tracking-wider block font-semibold">
                    Fuel & Operating Cost
                  </span>
                  <span className="text-2xl font-bold font-mono text-semantic-red mt-1 block">
                    {prediction.expected_expenses_inr}
                  </span>
                  <span className="text-[10px] text-content-muted">Transit km consumption</span>
                </div>

                <div className="bg-surface-2/50 p-4 rounded-xl border border-lime/30 bg-lime-muted/20">
                  <span className="text-[10px] text-lime uppercase tracking-wider block font-bold">
                    Total Net Take-Home
                  </span>
                  <span className="text-2xl font-bold font-mono text-lime mt-1 block">
                    {prediction.expected_net_inr}
                  </span>
                  <span className="text-[10px] text-content-muted">Take-home bottom-line</span>
                </div>
              </div>

              {/* Advisory Disclaimer */}
              <div className="flex items-start space-x-2.5 text-xs text-content-muted bg-surface-2/40 p-3.5 rounded-xl border border-hairline">
                <ShieldAlert className="w-4 h-4 text-lime shrink-0 mt-0.5" />
                <p className="text-[11px] leading-relaxed">
                  <strong>Decision-Support Advisory:</strong> This estimate is generated by machine learning trained on baseline Bangalore observations. Weather conditions, surge incentives, and order frequency fluctuate dynamically.
                </p>
              </div>
            </div>
          ) : (
            <div className="bg-surface-1 border border-hairline rounded-2xl p-16 text-center space-y-4 shadow-card">
              <div className="w-14 h-14 rounded-full bg-surface-2 border border-hairline flex items-center justify-center mx-auto text-lime">
                <Zap className="w-7 h-7" />
              </div>
              <h3 className="text-sm font-semibold text-content-primary">Inference Ready</h3>
              <p className="text-xs text-content-muted max-w-md mx-auto leading-relaxed">
                Select your platform, Bangalore zone, and duration to run the point-in-time quantile model and inspect expected take-home distributions.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
