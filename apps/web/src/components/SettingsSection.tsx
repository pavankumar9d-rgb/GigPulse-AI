"use client";

import React, { useState } from "react";
import {
  AlertTriangle,
  CheckCircle,
  Database,
  Download,
  Lock,
  Settings,
  ShieldAlert,
  Trash2,
} from "lucide-react";
import { api } from "../lib/api";

interface SettingsProps {
  workerRef: string;
  onRefreshData: () => void;
}

export const SettingsSection: React.FC<SettingsProps> = ({ workerRef, onRefreshData }) => {
  const [isExporting, setIsExporting] = useState<boolean>(false);
  const [exportMessage, setExportMessage] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);
  const [deleteConfirmed, setDeleteConfirmed] = useState<boolean>(false);
  const [deleteMessage, setDeleteMessage] = useState<string | null>(null);

  const handleExport = async () => {
    setIsExporting(true);
    setExportMessage(null);
    try {
      const data = await api.exportData(workerRef);
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `gigpulse_export_${workerRef}_${new Date().toISOString().slice(0, 10)}.json`;
      a.click();
      URL.revokeObjectURL(url);
      setExportMessage(`Successfully exported ${data.counts.deliveries} deliveries and ${data.counts.work_sessions} sessions.`);
    } catch (err: any) {
      setExportMessage(`Export failed: ${err.message}`);
    } finally {
      setIsExporting(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteConfirmed) return;
    setIsDeleting(true);
    setDeleteMessage(null);
    try {
      const res = await api.deleteAccountData(workerRef);
      setDeleteMessage(`Purged: ${res.deleted_counts.deliveries} deliveries, ${res.deleted_counts.work_sessions} sessions, ${res.deleted_counts.expenses} expenses.`);
      setDeleteConfirmed(false);
      onRefreshData();
    } catch (err: any) {
      setDeleteMessage(`Deletion failed: ${err.message}`);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="p-5 md:p-8 space-y-6 max-w-[1600px] mx-auto select-none">
      <div>
        <h2 className="text-xl font-bold tracking-tight text-content-primary flex items-center space-x-2">
          <span>Worker Settings & Privacy Governance</span>
        </h2>
        <p className="text-xs text-content-muted mt-0.5">
          Owner-scoped operational privacy, structured data export, and complete record deletion controls
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Worker & Currency Settings */}
        <div className="bg-surface-1 border border-hairline rounded-2xl p-6 space-y-5 shadow-card">
          <div className="flex items-center justify-between border-b border-hairline/60 pb-3">
            <h3 className="text-xs font-semibold text-content-primary uppercase tracking-wider">
              Profile & Runtime Parameters
            </h3>
            <span className="text-[10px] font-mono text-lime bg-lime-muted px-2.5 py-0.5 rounded-full border border-lime/30">
              Active Scope
            </span>
          </div>

          <div className="space-y-3.5 text-xs">
            <div>
              <span className="text-content-muted text-[10px] uppercase font-semibold block">Active Worker Identifier</span>
              <span className="font-mono text-content-primary font-bold mt-1 block text-sm">{workerRef}</span>
            </div>
            <div>
              <span className="text-content-muted text-[10px] uppercase font-semibold block">Operating Currency</span>
              <span className="font-mono text-content-primary font-bold mt-1 block">INR (Indian Rupee, ₹)</span>
            </div>
            <div>
              <span className="text-content-muted text-[10px] uppercase font-semibold block">Arithmetic Precision</span>
              <span className="font-mono text-lime font-bold mt-1 block">64-bit Integer Minor Units (Paise)</span>
            </div>
            <div>
              <span className="text-content-muted text-[10px] uppercase font-semibold block">Study Region</span>
              <span className="font-mono text-content-primary font-bold mt-1 block">Bangalore Metro Area (H3 & Hex Zones)</span>
            </div>
          </div>

          <div className="border-t border-hairline/60 pt-4 text-[11px] text-content-muted space-y-1">
            <span className="font-semibold text-content-primary block text-[10px] uppercase tracking-wider">Zero Floating-Point Financials:</span>
            <p className="text-[10px] leading-relaxed">All ledger entries and calculations use integer paise to eliminate floating-point precision drift across multi-platform earnings.</p>
          </div>
        </div>

        {/* Data Governance & Export */}
        <div className="bg-surface-1 border border-hairline rounded-2xl p-6 space-y-5 shadow-card">
          <div className="flex items-center justify-between border-b border-hairline/60 pb-3">
            <h3 className="text-xs font-semibold text-content-primary uppercase tracking-wider">
              Data Portability & Governance
            </h3>
            <span className="text-[10px] font-mono text-content-muted bg-surface-2 px-2.5 py-0.5 rounded-full border border-hairline">
              GDPR Compatible
            </span>
          </div>

          <p className="text-xs text-content-muted leading-relaxed">
            Download your entire operational history, dispatches, shift intervals, and expense receipts in portable JSON format.
          </p>

          <button
            onClick={handleExport}
            disabled={isExporting}
            className="w-full py-3 bg-surface-2 hover:bg-surface-hover border border-hairline hover:border-lime/40 text-content-primary font-bold rounded-full text-xs uppercase tracking-wider transition-all shadow-card flex items-center justify-center space-x-2 disabled:opacity-50"
          >
            <Download className="w-4 h-4 text-lime" />
            <span>{isExporting ? "Generating Export Package..." : "Export Worker Records (JSON)"}</span>
          </button>

          {exportMessage && (
            <div className="p-3.5 bg-lime-muted/20 border border-lime/30 rounded-xl text-xs text-lime flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 shrink-0" />
              <span>{exportMessage}</span>
            </div>
          )}

          {/* Destructive Deletion Box */}
          <div className="border-t border-semantic-red/30 pt-4 mt-4 space-y-3">
            <h4 className="text-[10px] font-bold text-semantic-red uppercase tracking-wider flex items-center space-x-1.5">
              <AlertTriangle className="w-4 h-4" />
              <span>Permanent Account Data Purge</span>
            </h4>
            <p className="text-[10px] text-content-muted leading-relaxed">
              Irreversibly delete all work sessions, deliveries, and expenses associated with profile {workerRef}.
            </p>

            <div className="flex items-center space-x-2 text-xs">
              <input
                type="checkbox"
                id="confirmDelete"
                checked={deleteConfirmed}
                onChange={(e) => setDeleteConfirmed(e.target.checked)}
                className="accent-semantic-red rounded cursor-pointer"
              />
              <label htmlFor="confirmDelete" className="text-content-muted text-[11px] cursor-pointer">
                I understand this will permanently delete all records for {workerRef}
              </label>
            </div>

            <button
              onClick={handleDelete}
              disabled={isDeleting || !deleteConfirmed}
              className="w-full py-2.5 bg-semantic-red/10 text-semantic-red border border-semantic-red/30 font-bold rounded-full text-xs uppercase tracking-wider hover:bg-semantic-red hover:text-white transition-all shadow disabled:opacity-30 flex items-center justify-center space-x-2"
            >
              <Trash2 className="w-4 h-4" />
              <span>{isDeleting ? "Purging Records..." : "Execute Confirmed Deletion"}</span>
            </button>

            {deleteMessage && (
              <div className="p-3 bg-surface-2 rounded-xl text-xs text-content-muted font-mono">
                {deleteMessage}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
