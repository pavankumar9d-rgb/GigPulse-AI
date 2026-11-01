"use client";

import React from "react";

export type DataSourceType =
  | "REAL_DEVICE"
  | "EXTERNAL_LIVE"
  | "DATABASE"
  | "SYNTHETIC_RESEARCH"
  | "MODEL_PREDICTIONS"
  | "OFFLINE_CACHED";

interface DataBadgeProps {
  type: DataSourceType;
  label?: string;
  className?: string;
}

export const DataBadge: React.FC<DataBadgeProps> = ({ type, label, className = "" }) => {
  const configs: Record<DataSourceType, { text: string; bg: string; textCol: string; border: string }> = {
    REAL_DEVICE: {
      text: "REAL DEVICE DATA",
      bg: "bg-cyan-950/60",
      textCol: "text-cyan-400",
      border: "border-cyan-400/40",
    },
    EXTERNAL_LIVE: {
      text: "EXTERNAL LIVE DATA",
      bg: "bg-emerald-950/60",
      textCol: "text-emerald-400",
      border: "border-emerald-400/40",
    },
    DATABASE: {
      text: "DATABASE DATA",
      bg: "bg-indigo-950/60",
      textCol: "text-indigo-400",
      border: "border-indigo-400/40",
    },
    SYNTHETIC_RESEARCH: {
      text: "SYNTHETIC RESEARCH DATA",
      bg: "bg-amber-950/50",
      textCol: "text-amber-400",
      border: "border-amber-400/30",
    },
    MODEL_PREDICTIONS: {
      text: "MODEL PREDICTIONS",
      bg: "bg-lime-muted",
      textCol: "text-lime",
      border: "border-lime/30",
    },
    OFFLINE_CACHED: {
      text: "CACHED OFFLINE DATA",
      bg: "bg-neutral-800/80",
      textCol: "text-neutral-400",
      border: "border-neutral-700",
    },
  };

  const c = configs[type] || configs.DATABASE;

  return (
    <span
      className={`inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-mono uppercase tracking-wider font-semibold border ${c.bg} ${c.textCol} ${c.border} ${className}`}
    >
      {label || c.text}
    </span>
  );
};

