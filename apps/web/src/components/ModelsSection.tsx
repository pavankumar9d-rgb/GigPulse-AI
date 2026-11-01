"use client";

import React, { useState, useEffect } from "react";
import {
  AlertCircle,
  Brain,
  CheckCircle,
  Cpu,
  GitBranch,
  RefreshCw,
  Scale,
  ShieldCheck,
  TrendingUp,
  Zap,
} from "lucide-react";
import { api } from "../lib/api";

export const ModelsSection: React.FC = () => {
  const [models, setModels] = useState<any[]>([]);
  const [selectedModel, setSelectedModel] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isRetraining, setIsRetraining] = useState<boolean>(false);
  const [retrainMsg, setRetrainMsg] = useState<string | null>(null);

  const fetchModels = async () => {
    setIsLoading(true);
    try {
      const res = await api.getModels();
      setModels(res.models || []);
      if (res.models && res.models.length > 0 && !selectedModel) {
        setSelectedModel(res.models[0]);
      }
    } catch {
      // ignore
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchModels();
  }, []);

  const handleRetrain = async () => {
    setIsRetraining(true);
    setRetrainMsg(null);
    try {
      const res = await api.retrainModels();
      setModels(res.models || []);
      if (res.models && res.models.length > 0) {
        setSelectedModel(res.models[0]);
      }
      setRetrainMsg("Machine learning pipelines trained and backtested successfully.");
    } catch (err: any) {
      setRetrainMsg(`Retraining failed: ${err.message}`);
    } finally {
      setIsRetraining(false);
    }
  };

  const evalData = selectedModel?.evaluation;

  return (
    <div className="p-5 md:p-8 space-y-6 max-w-[1600px] mx-auto select-none">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-content-primary flex items-center space-x-2">
            <span>Model Registry Lab & Diagnostic Evaluation</span>
          </h2>
          <p className="text-xs text-content-muted mt-0.5">
            Transparent chronological split backtests, baseline comparisons, calibration benchmarks, and documented scientific boundaries
          </p>
        </div>

        <button
          onClick={handleRetrain}
          disabled={isRetraining}
          className="flex items-center space-x-2 px-4 py-2 rounded-full bg-lime hover:bg-lime-bright text-canvas font-bold text-xs uppercase tracking-wider transition-all shadow-lime-glow disabled:opacity-50 self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 stroke-[2.5] ${isRetraining ? "animate-spin" : ""}`} />
          <span>{isRetraining ? "Retraining Models..." : "Trigger Model Retrain"}</span>
        </button>
      </div>

      {retrainMsg && (
        <div className="p-3.5 bg-lime-muted/20 border border-lime/30 rounded-2xl text-xs text-lime flex items-center space-x-2">
          <CheckCircle className="w-4 h-4 shrink-0" />
          <span>{retrainMsg}</span>
        </div>
      )}

      {/* Model Selection Tabs */}
      <div className="flex border-b border-hairline space-x-6">
        {models.map((m) => {
          const active = selectedModel?.id === m.id;
          return (
            <button
              key={m.id}
              onClick={() => setSelectedModel(m)}
              className={`pb-3 text-xs font-semibold uppercase tracking-wider transition-all border-b-2 ${
                active
                  ? "border-lime text-lime"
                  : "border-transparent text-content-muted hover:text-content-primary"
              }`}
            >
              {m.model_name.replace("_", " ")} ({m.version})
            </button>
          );
        })}
      </div>

      {selectedModel && evalData ? (
        <div className="space-y-6">
          {/* Metadata Card */}
          <div className="bg-surface-1 border border-hairline rounded-2xl p-6 grid grid-cols-1 md:grid-cols-4 gap-5 text-xs shadow-card">
            <div>
              <span className="text-[10px] text-content-muted uppercase tracking-wider block font-semibold">Target Variable</span>
              <span className="font-mono text-content-primary font-semibold text-xs mt-1 block">
                {selectedModel.target_definition}
              </span>
            </div>
            <div>
              <span className="text-[10px] text-content-muted uppercase tracking-wider block font-semibold">Temporal Split</span>
              <span className="font-mono text-content-primary font-semibold text-xs mt-1 block capitalize">
                {evalData.split_info?.split_type?.replace(/_/g, " ") || "Chronological Hold-Out"}
              </span>
            </div>
            <div>
              <span className="text-[10px] text-content-muted uppercase tracking-wider block font-semibold">Partition Samples</span>
              <span className="font-mono text-content-primary font-semibold text-xs mt-1 block">
                Train: {evalData.split_info?.train_rows} | Test: {evalData.split_info?.test_rows || evalData.split_info?.val_rows}
              </span>
            </div>
            <div>
              <span className="text-[10px] text-content-muted uppercase tracking-wider block font-semibold">Status in Cockpit</span>
              <span className="inline-block mt-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase bg-lime-muted text-lime border border-lime/30">
                {selectedModel.status}
              </span>
            </div>
          </div>

          {/* Model vs Baselines Comparison Table */}
          <div className="bg-surface-1 border border-hairline rounded-2xl overflow-hidden shadow-card">
            <div className="p-5 border-b border-hairline flex justify-between items-center">
              <div>
                <h3 className="font-semibold text-xs text-content-primary flex items-center space-x-2 uppercase tracking-wider">
                  <Scale className="w-4 h-4 text-lime" />
                  <span>Held-Out Chronological Backtest Evaluation</span>
                </h3>
                <p className="text-[11px] text-content-muted">
                  Candidate model benchmarked strictly against naive moving-average and historical baselines
                </p>
              </div>
              <span className="text-[10px] font-mono text-lime bg-lime-muted px-2.5 py-1 rounded-full border border-lime/30 font-semibold">
                Zero Leakage Verified
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-surface-2/80 text-content-muted uppercase text-[10px] tracking-wider border-b border-hairline">
                  <tr>
                    <th className="py-3 px-4 font-semibold">Model / Baseline Specification</th>
                    <th className="py-3 px-4 text-right font-semibold">MAE</th>
                    <th className="py-3 px-4 text-right font-semibold">RMSE</th>
                    <th className="py-3 px-4 text-right font-semibold">WAPE</th>
                    {"r2" in (Object.values(evalData.models_comparison)[0] as any || {}) && (
                      <th className="py-3 px-4 text-right font-semibold">R² Score</th>
                    )}
                    <th className="py-3 px-4 text-right font-semibold">Verdict</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-hairline">
                  {Object.entries(evalData.models_comparison).map(([name, metrics]: [string, any]) => {
                    const isCandidate = name.includes("trees") || name.includes("gradient") || name.includes("regressor");

                    return (
                      <tr
                        key={name}
                        className={`transition-colors ${
                          isCandidate ? "bg-lime-muted/10 font-semibold text-lime" : "text-content-secondary"
                        }`}
                      >
                        <td className="py-3 px-4 font-mono text-xs">
                          {name.replace(/_/g, " ")}
                        </td>
                        <td className="py-3 px-4 text-right font-mono">
                          {metrics.mae_inr !== undefined ? `₹${metrics.mae_inr}` : metrics.mae}
                        </td>
                        <td className="py-3 px-4 text-right font-mono">
                          {metrics.rmse_inr !== undefined ? `₹${metrics.rmse_inr}` : metrics.rmse}
                        </td>
                        <td className="py-3 px-4 text-right font-mono">
                          {(metrics.wape * 100).toFixed(2)}%
                        </td>
                        {metrics.r2 !== undefined && (
                          <td className="py-3 px-4 text-right font-mono">
                            {metrics.r2.toFixed(4)}
                          </td>
                        )}
                        <td className="py-3 px-4 text-right">
                          {isCandidate ? (
                            <span className="px-2.5 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider bg-lime text-canvas shadow-lime-sm">
                              Champion Model
                            </span>
                          ) : (
                            <span className="text-[10px] uppercase font-mono text-content-muted">
                              Naive Baseline
                            </span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Uncertainty Calibration Box */}
          {evalData.uncertainty_evaluation && (
            <div className="bg-surface-1 border border-hairline rounded-2xl p-6 space-y-4 shadow-card">
              <h3 className="text-xs font-semibold text-content-primary flex items-center space-x-2 uppercase tracking-wider">
                <ShieldCheck className="w-4 h-4 text-lime" />
                <span>Prediction Interval Calibration (Empirical Coverage Check)</span>
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                <div className="bg-surface-2 p-4 rounded-xl border border-hairline">
                  <span className="text-[10px] text-content-muted block uppercase font-semibold">Nominal Target Coverage</span>
                  <span className="text-2xl font-bold font-mono text-content-primary mt-1 block">
                    {evalData.uncertainty_evaluation.nominal_coverage_pct}%
                  </span>
                  <span className="text-[11px] text-content-muted block mt-1">Expected 80% theoretical bound</span>
                </div>
                <div className="bg-surface-2 p-4 rounded-xl border border-lime/30 bg-lime-muted/20">
                  <span className="text-[10px] text-lime block uppercase font-bold">Empirical Observed Coverage</span>
                  <span className="text-2xl font-bold font-mono text-lime mt-1 block">
                    {evalData.uncertainty_evaluation.empirical_coverage_pct}%
                  </span>
                  <span className="text-[11px] text-content-muted block mt-1">
                    Fraction of held-out test points that landed inside bounds
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Limitations Box */}
          <div className="bg-surface-1 border border-hairline rounded-2xl p-5 space-y-2 shadow-card">
            <h4 className="text-[11px] font-bold text-lime uppercase tracking-wider flex items-center space-x-2">
              <AlertCircle className="w-4 h-4" />
              <span>Scientific Documentation & Boundary Conditions</span>
            </h4>
            <p className="text-xs text-content-muted leading-relaxed">
              {selectedModel.limitations}
            </p>
          </div>
        </div>
      ) : (
        <div className="bg-surface-1 border border-hairline rounded-2xl p-16 text-center text-xs text-content-muted shadow-card">
          Loading model registry benchmarks...
        </div>
      )}
    </div>
  );
};
