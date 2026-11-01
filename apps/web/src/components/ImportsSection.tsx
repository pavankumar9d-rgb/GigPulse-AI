"use client";

import React, { useState } from "react";
import {
  AlertTriangle,
  ArrowRight,
  CheckCircle,
  FileSpreadsheet,
  FileUp,
  ShieldCheck,
  UploadCloud,
} from "lucide-react";
import { api } from "../lib/api";

export const ImportsSection: React.FC = () => {
  const [templateType, setTemplateType] = useState<string>("work_sessions");
  const [csvContent, setCsvContent] = useState<string>("");
  const [validationReport, setValidationReport] = useState<any | null>(null);
  const [commitResult, setCommitResult] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const sampleCsvs: Record<string, string> = {
    work_sessions: `worker_ref,platform_code,started_at,ended_at,status,source_type,timezone
worker_w01,flash_drop,2026-11-02T10:00:00+05:30,2026-11-02T14:00:00+05:30,completed,manual,Asia/Kolkata
worker_w01,swift_bite,2026-11-02T18:00:00+05:30,2026-11-02T22:00:00+05:30,completed,manual,Asia/Kolkata`,
    deliveries: `worker_ref,platform_code,session_ref,accepted_at,completed_at,pickup_zone_code,drop_zone_code,payout_paise,incentive_paise,tip_paise,distance_m,duration_seconds,status,target_quality,source_type
worker_w01,flash_drop,sess_user_01,2026-11-02T10:15:00+05:30,2026-11-02T10:45:00+05:30,zone_koramangala,zone_indiranagar,12500,2000,500,4500,1800,completed,user_reported,manual`,
    expenses: `worker_ref,session_ref,occurred_at,category,amount_paise,source_type,notes
worker_w01,sess_user_01,2026-11-02T11:00:00+05:30,fuel,35000,manual,Petrol refill 3.2L`,
    zone_demand: `zone_code,interval_start,interval_minutes,orders_requested,orders_completed,deliveries_observed,demand_proxy_value,target_type,coverage_fraction,target_quality,source_type
HYD_ZONE_01,2026-11-02T18:00:00+05:30,30,25,22,22,22.0,observed_deliveries,1.0,user_reported,manual`,
  };

  const handleLoadSample = () => {
    setCsvContent(sampleCsvs[templateType]);
    setValidationReport(null);
    setCommitResult(null);
    setError(null);
  };

  const handleValidate = async () => {
    if (!csvContent.trim()) {
      setError("Please enter or paste CSV content before validating.");
      return;
    }
    setIsLoading(true);
    setError(null);
    setCommitResult(null);

    try {
      const res = await api.validateImport(csvContent, templateType, `${templateType}_user_upload.csv`);
      setValidationReport(res);
    } catch (err: any) {
      setError(err.message || "Failed to validate CSV.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCommit = async () => {
    if (!validationReport?.batch_id) return;
    setIsLoading(true);
    setError(null);

    try {
      const res = await api.commitImport(validationReport.batch_id);
      setCommitResult(res);
    } catch (err: any) {
      setError(err.message || "Failed to commit import.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-5 md:p-8 space-y-6 max-w-[1600px] mx-auto select-none">
      <div>
        <h2 className="text-xl font-bold tracking-tight text-content-primary flex items-center space-x-2">
          <span>Safe Data Ingestion & Validation Gateway</span>
        </h2>
        <p className="text-xs text-content-muted mt-0.5">
          Deterministic 3-step import pipeline with formula-injection neutralization, SHA-256 deduplication, and zero unconfirmed writes
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input & Upload Column */}
        <div className="bg-surface-1 border border-hairline rounded-2xl p-6 space-y-5 shadow-card">
          <div className="flex justify-between items-center border-b border-hairline/60 pb-3">
            <h3 className="text-xs font-semibold text-content-primary uppercase tracking-wider">
              Step 1: Input Payload
            </h3>
            <button
              onClick={handleLoadSample}
              className="text-xs text-lime hover:underline font-bold"
            >
              Load Sample CSV
            </button>
          </div>

          <div>
            <label className="text-[11px] font-medium text-content-muted block mb-1.5 uppercase tracking-wider">
              Schema Target Contract
            </label>
            <select
              value={templateType}
              onChange={(e) => {
                setTemplateType(e.target.value);
                setValidationReport(null);
                setCommitResult(null);
              }}
              className="w-full bg-surface-2 border border-hairline rounded-xl px-3.5 py-2.5 text-xs text-content-primary focus:outline-none focus:border-lime cursor-pointer"
            >
              <option value="work_sessions" className="bg-surface-1">work_sessions (Online shifts & intervals)</option>
              <option value="deliveries" className="bg-surface-1">deliveries (Payouts, incentives, tips)</option>
              <option value="expenses" className="bg-surface-1">expenses (Fuel, servicing, equipment)</option>
              <option value="zone_demand" className="bg-surface-1">zone_demand (Spatial counts & activity)</option>
            </select>
          </div>

          <div>
            <label className="text-[11px] font-medium text-content-muted block mb-1.5 uppercase tracking-wider">
              Raw CSV Content
            </label>
            <textarea
              rows={9}
              value={csvContent}
              onChange={(e) => setCsvContent(e.target.value)}
              placeholder="worker_ref,platform_code,started_at,ended_at..."
              className="w-full bg-canvas border border-hairline rounded-xl p-3.5 text-xs font-mono text-content-primary focus:outline-none focus:border-lime resize-y"
            />
          </div>

          <button
            onClick={handleValidate}
            disabled={isLoading || !csvContent.trim()}
            className="w-full py-3 bg-surface-2 hover:bg-surface-hover border border-hairline hover:border-lime/40 text-content-primary font-bold rounded-full text-xs uppercase tracking-wider transition-all shadow-card disabled:opacity-50 flex items-center justify-center space-x-2"
          >
            <FileUp className="w-4 h-4 text-lime" />
            <span>Validate Schema & Sanitize Payload</span>
          </button>

          {error && (
            <div className="p-3 bg-semantic-red/10 border border-semantic-red/30 rounded-xl text-xs text-semantic-red">
              {error}
            </div>
          )}
        </div>

        {/* Validation Report & Commit Column */}
        <div className="space-y-4">
          {validationReport ? (
            <div className="bg-surface-1 border border-hairline rounded-2xl p-6 space-y-5 shadow-card relative overflow-hidden">
              <div className="flex justify-between items-center pb-3 border-b border-hairline">
                <h3 className="text-xs font-semibold text-content-primary flex items-center space-x-2 uppercase tracking-wider">
                  <ShieldCheck className="w-4 h-4 text-lime" />
                  <span>Step 2: Validation Audit Report</span>
                </h3>
                <span className="text-[11px] font-mono text-content-muted bg-surface-2 px-2.5 py-0.5 rounded-full border border-hairline">
                  Batch: {validationReport.batch_id.slice(0, 8)}
                </span>
              </div>

              {/* Row Counts Matrix */}
              <div className="grid grid-cols-4 gap-3 text-center text-xs">
                <div className="bg-surface-2 p-3 rounded-xl border border-hairline">
                  <span className="text-[10px] text-content-muted uppercase block font-semibold">Total</span>
                  <span className="text-lg font-bold font-mono text-content-primary mt-1 block">{validationReport.total_rows}</span>
                </div>
                <div className="bg-surface-2 p-3 rounded-xl border border-lime/30 bg-lime-muted/20">
                  <span className="text-[10px] text-lime uppercase block font-bold">Accepted</span>
                  <span className="text-lg font-bold font-mono text-lime mt-1 block">{validationReport.accepted_rows}</span>
                </div>
                <div className="bg-surface-2 p-3 rounded-xl border border-semantic-red/30">
                  <span className="text-[10px] text-semantic-red uppercase block font-semibold">Rejected</span>
                  <span className="text-lg font-bold font-mono text-semantic-red mt-1 block">{validationReport.rejected_rows}</span>
                </div>
                <div className="bg-surface-2 p-3 rounded-xl border border-semantic-amber/30">
                  <span className="text-[10px] text-semantic-amber uppercase block font-semibold">Duplicates</span>
                  <span className="text-lg font-bold font-mono text-semantic-amber mt-1 block">{validationReport.duplicate_rows}</span>
                </div>
              </div>

              {/* Security Audit Checklist */}
              <div className="bg-surface-2/60 p-4 rounded-xl border border-hairline text-[11px] space-y-1.5 text-content-muted">
                <div className="flex items-center space-x-2 text-content-primary font-medium">
                  <CheckCircle className="w-3.5 h-3.5 text-lime" />
                  <span>CSV Injection Neutralized: Leading =, +, -, @ characters sanitized</span>
                </div>
                <div className="flex items-center space-x-2 text-content-primary font-medium">
                  <CheckCircle className="w-3.5 h-3.5 text-lime" />
                  <span>Cryptographic Deduplication: SHA-256 fingerprint verified</span>
                </div>
                <div className="flex items-center space-x-2 text-lime font-medium">
                  <CheckCircle className="w-3.5 h-3.5 text-lime" />
                  <span>Zero Unconfirmed Writes: Awaiting your manual confirmation below</span>
                </div>
              </div>

              {/* Step 3: Explicit Commit Action */}
              <div className="pt-2">
                {commitResult ? (
                  <div className="p-4 bg-lime-muted/20 border border-lime/40 rounded-xl text-xs text-lime space-y-1">
                    <div className="font-bold flex items-center space-x-2">
                      <CheckCircle className="w-4 h-4" />
                      <span>Batch Committed to SQLite Database!</span>
                    </div>
                    <p className="text-[11px] text-content-secondary">
                      {commitResult.accepted_count} operational records persisted into database tables.
                    </p>
                  </div>
                ) : (
                  <button
                    onClick={handleCommit}
                    disabled={isLoading || validationReport.accepted_rows === 0}
                    className="w-full py-3 bg-lime hover:bg-lime-bright text-canvas font-bold rounded-full text-xs uppercase tracking-wider transition-all shadow-lime-glow disabled:opacity-50 flex items-center justify-center space-x-2"
                  >
                    <UploadCloud className="w-4 h-4 stroke-[2.5]" />
                    <span>Step 3: Commit {validationReport.accepted_rows} Rows to Database</span>
                  </button>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-surface-1 border border-hairline rounded-2xl p-16 text-center space-y-4 shadow-card">
              <div className="w-14 h-14 rounded-full bg-surface-2 border border-hairline flex items-center justify-center mx-auto text-lime">
                <ShieldCheck className="w-7 h-7" />
              </div>
              <h3 className="text-sm font-semibold text-content-primary">Pipeline Ready</h3>
              <p className="text-xs text-content-muted max-w-sm mx-auto leading-relaxed">
                Paste or load sample CSV on the left to preview validation reports, audit checksums, and row deductions before committing.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
