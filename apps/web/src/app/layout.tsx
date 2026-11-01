import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GigPulse AI — Mobility Operations Cockpit",
  description:
    "AI-Driven Spatio-Temporal Earnings Prediction, Demand Forecasting & Multi-Platform Optimizer",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-canvas text-content-primary antialiased selection:bg-lime selection:text-canvas">
        {/* Subtle, refined research baseline indicator */}
        <div className="bg-canvas-subtle/80 border-b border-hairline/60 px-4 py-1.5 text-[11px] flex items-center justify-between z-50 text-content-muted backdrop-blur-sm">
          <div className="flex items-center space-x-2.5">
            <span className="inline-block w-1.5 h-1.5 rounded-full bg-lime shadow-lime-sm animate-lime-pulse" />
            <span className="font-medium text-content-primary tracking-wide text-[10px] uppercase">
              Academic Research Prototype
            </span>
            <span className="text-hairline-strong">|</span>
            <span className="hidden md:inline text-content-secondary text-[11px]">
              Bangalore Study Area (Synthetic Baseline Seed=42) • Decision-Support Advisory Engine
            </span>
          </div>
          <div className="flex items-center space-x-2 text-[10px] font-mono text-content-muted">
            <span className="bg-surface-2 px-2 py-0.5 rounded-full border border-hairline text-content-secondary">
              FastAPI • SQLite / PostgreSQL
            </span>
          </div>
        </div>
        {children}
      </body>
    </html>
  );
}
