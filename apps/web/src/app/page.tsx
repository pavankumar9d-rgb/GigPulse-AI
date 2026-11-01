"use client";

import React, { useEffect, useState } from "react";
import { Navbar, NavTab } from "../components/Navbar";
import { OverviewSection } from "../components/OverviewSection";
import { EarningsSection } from "../components/EarningsSection";
import { PredictionSection } from "../components/PredictionSection";
import { DeliveriesSection } from "../components/DeliveriesSection";
import { DemandSection } from "../components/DemandSection";
import { PlatformsSection } from "../components/PlatformsSection";
import { RecommendationsSection } from "../components/RecommendationsSection";
import { ExpensesSection } from "../components/ExpensesSection";
import { ImportsSection } from "../components/ImportsSection";
import { ModelsSection } from "../components/ModelsSection";
import { SettingsSection } from "../components/SettingsSection";
import { api } from "../lib/api";
import { ChevronDown, Search, ShieldAlert, Sparkles, User, WifiOff } from "lucide-react";
import { DeviceLocation } from "../hooks/useGeolocation";
import { getOfflineSnapshot, saveOfflineSnapshot } from "../lib/offlineStore";
import { DataBadge } from "../components/DataBadge";

export default function DashboardPage() {
  const [currentTab, setCurrentTab] = useState<NavTab>("overview");
  const [workerRef, setWorkerRef] = useState<string>("worker_w01");
  const [workers, setWorkers] = useState<Array<{ worker_ref: string; display_name: string }>>([]);

  const [summary, setSummary] = useState<any | null>(null);
  const [recommendations, setRecommendations] = useState<any | null>(null);
  const [deliveries, setDeliveries] = useState<any[]>([]);
  const [expenses, setExpenses] = useState<any[]>([]);
  const [earningsHistory, setEarningsHistory] = useState<any[]>([]);
  const [weeklySummary, setWeeklySummary] = useState<any | null>(null);
  const [deviceLocation, setDeviceLocation] = useState<DeviceLocation | null>(null);

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isOffline, setIsOffline] = useState<boolean>(false);
  const [backendError, setBackendError] = useState<string | null>(null);

  const loadData = async () => {
    setIsLoading(true);
    setBackendError(null);

    try {
      // 1. Fetch available workers
      try {
        const workersRes = await api.getWorkers();
        if (workersRes?.items && workersRes.items.length > 0) {
          setWorkers(workersRes.items);
        }
      } catch {
        setWorkers([{ worker_ref: "worker_w01", display_name: "Rider W01" }]);
      }

      // 2. Fetch dashboard summary & weekly rolling analytics
      const [sum, weekly] = await Promise.all([
        api.getDashboardSummary(workerRef),
        api.getWeeklyEarnings(workerRef).catch(() => null),
      ]);
      setSummary(sum);
      setWeeklySummary(weekly);

      // 3. Fetch deliveries & expenses
      const [delivRes, expRes, histRes] = await Promise.all([
        api.getDeliveries(workerRef, 100).catch(() => ({ items: [] })),
        api.getExpenses(workerRef, 100).catch(() => ({ items: [] })),
        api.getEarningsHistory(workerRef).catch(() => ({ items: [] })),
      ]);

      const fetchedDeliveries = delivRes.items || [];
      const fetchedExpenses = expRes.items || [];
      const fetchedHistory = histRes.items || [];

      setDeliveries(fetchedDeliveries);
      setExpenses(fetchedExpenses);
      setEarningsHistory(fetchedHistory);

      // 4. Preload top opportunity recommendation
      try {
        const now = new Date();
        now.setHours(18, 0, 0, 0);
        const startAt = new Date(now.getTime() + 24 * 3600 * 1000);
        const endAt = new Date(startAt.getTime() + 4 * 3600 * 1000);

        const rec = await api.getRecommendations({
          worker_ref: workerRef,
          candidate_platform_ids: ["flash_drop", "swift_bite", "hyper_courier"],
          candidate_zone_ids: ["zone_koramangala", "zone_indiranagar", "zone_hsr"],
          time_window: {
            start_at: startAt.toISOString(),
            end_at: endAt.toISOString(),
          },
          preferences: {
            min_net_earnings_paise_per_hour: 8000,
            max_travel_distance_m: 12000,
            risk_tolerance: "balanced",
          },
        });
        setRecommendations(rec);

        // Cache full offline snapshot in IndexedDB
        saveOfflineSnapshot(`dashboard_${workerRef}`, {
          summary: sum,
          weeklySummary: weekly,
          deliveries: fetchedDeliveries,
          expenses: fetchedExpenses,
          earningsHistory: fetchedHistory,
          recommendations: rec,
        });
      } catch {
        // Recommendations non-blocking
      }
      setIsOffline(false);
    } catch (err: any) {
      // Offline fallback: Attempt to load from IndexedDB snapshot
      const cached = await getOfflineSnapshot<any>(`dashboard_${workerRef}`);
      if (cached?.data) {
        setSummary(cached.data.summary);
        setWeeklySummary(cached.data.weeklySummary);
        setDeliveries(cached.data.deliveries || []);
        setExpenses(cached.data.expenses || []);
        setEarningsHistory(cached.data.earningsHistory || []);
        setRecommendations(cached.data.recommendations || null);
        setIsOffline(true);
      } else {
        setBackendError(
          err.message || "Failed to connect to FastAPI backend. Ensure python services/api/main.py is running."
        );
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [workerRef]);

  // Visibility-Aware 30s Polling & PWA Service Worker Registration
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;

    const startPolling = () => {
      if (!interval) {
        interval = setInterval(() => {
          if (document.visibilityState === "visible") {
            loadData();
          }
        }, 30000);
      }
    };

    const stopPolling = () => {
      if (interval) {
        clearInterval(interval);
        interval = null;
      }
    };

    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible") {
        loadData();
        startPolling();
      } else {
        stopPolling();
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    startPolling();

    // Register service worker if supported
    if (typeof window !== "undefined" && "serviceWorker" in navigator) {
      navigator.serviceWorker.register("/sw.js").catch(() => {});
    }

    return () => {
      stopPolling();
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [workerRef]);

  // Section display names for top breadcrumb
  const sectionLabels: Record<NavTab, string> = {
    overview: "Operations Cockpit",
    earnings: "Earnings Analytics",
    prediction: "Earnings Predictor",
    deliveries: "Delivery Activity",
    demand: "Zone Demand Forecast",
    platforms: "Platform Benchmark",
    recommendations: "Opportunity Planner",
    expenses: "Operating Expenses",
    imports: "Data Pipeline",
    models: "Model Registry Lab",
    settings: "Worker & Governance",
  };

  const activeWorkerName =
    workers.find((w) => w.worker_ref === workerRef)?.display_name || "Arnold Aldridge (Rider W01)";

  return (
    <div className="flex flex-col md:flex-row min-h-screen bg-canvas text-content-primary">
      {/* Target screenshot icon rail */}
      <Navbar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        workerRef={workerRef}
        onSelectWorker={setWorkerRef}
        workers={workers}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Sleek Top Header Matching Target Reference */}
        <header className="h-16 border-b border-hairline/80 px-6 flex items-center justify-between shrink-0 bg-canvas/60 backdrop-blur-md z-20">
          <div className="flex items-center space-x-3">
            <h2 className="text-sm font-semibold tracking-tight text-content-primary">
              {sectionLabels[currentTab]}
            </h2>
            <span className="text-content-muted hidden sm:inline">•</span>
            <span className="text-[11px] text-content-muted hidden sm:inline font-mono">
              Academic Study Mesh
            </span>
            {isOffline && (
              <DataBadge type="OFFLINE_CACHED" label="OFFLINE / CACHED DATA" />
            )}
          </div>

          {/* Right Header: Search & Worker Profile Capsule */}
          <div className="flex items-center space-x-3.5">
            {/* Minimalist Search Button */}
            <button
              aria-label="Search"
              className="w-8 h-8 rounded-full bg-surface-1 border border-hairline hover:border-lime/40 text-content-secondary hover:text-content-primary flex items-center justify-center transition-colors"
            >
              <Search className="w-3.5 h-3.5" />
            </button>

            {/* Profile & Worker Switcher Capsule (Target Screenshot Style) */}
            <div className="flex items-center space-x-2.5 bg-surface-1 border border-hairline rounded-full pl-1.5 pr-3 py-1 hover:border-hairline-strong transition-colors">
              <div className="w-7 h-7 rounded-full bg-surface-2 border border-lime/30 flex items-center justify-center text-lime text-[11px] font-bold overflow-hidden shadow-inner">
                {/* Sleek monogram avatar */}
                <span>{activeWorkerName.slice(0, 2).toUpperCase()}</span>
              </div>
              <div className="text-left">
                <div className="flex items-center space-x-1.5">
                  <span className="text-xs font-semibold text-content-primary leading-tight">
                    {activeWorkerName.split(" ")[0]} {activeWorkerName.split(" ")[1] || ""}
                  </span>
                  <select
                    value={workerRef}
                    onChange={(e) => setWorkerRef(e.target.value)}
                    className="opacity-0 absolute inset-0 cursor-pointer"
                    title="Switch Worker"
                  >
                    {workers.map((w) => (
                      <option key={w.worker_ref} value={w.worker_ref} className="bg-surface-1 text-content-primary">
                        {w.display_name} ({w.worker_ref})
                      </option>
                    ))}
                  </select>
                </div>
                <div className="text-[10px] text-content-muted flex items-center space-x-1 leading-none mt-0.5">
                  <span className="text-lime font-bold">★ 4.9</span>
                  <span>rating</span>
                </div>
              </div>
              <ChevronDown className="w-3.5 h-3.5 text-content-muted pointer-events-none" />
            </div>
          </div>
        </header>

        {/* Content Body */}
        <main className="flex-1 overflow-y-auto">
          {backendError && (
            <div className="m-6 p-4 bg-semantic-red/10 border border-semantic-red/30 rounded-2xl text-xs text-semantic-red flex items-start space-x-3">
              <ShieldAlert className="w-4 h-4 shrink-0 mt-0.5" />
              <div>
                <strong className="block font-semibold">Backend Connection Offline:</strong>
                <p>{backendError}</p>
                <p className="text-[11px] text-content-muted mt-2">
                  Launch the FastAPI backend: <code className="bg-surface-2 px-1 py-0.5 rounded font-mono text-content-primary">python services/api/main.py</code>
                </p>
              </div>
            </div>
          )}

          {currentTab === "overview" && (
            <OverviewSection
              summary={summary}
              recommendations={recommendations}
              deliveries={deliveries}
              weeklySummary={weeklySummary}
              deviceLocation={deviceLocation}
              onLocationChange={setDeviceLocation}
              onNavigate={setCurrentTab}
              isLoading={isLoading}
              isOffline={isOffline}
            />
          )}

          {currentTab === "earnings" && (
            <EarningsSection
              summary={summary}
              earningsHistory={earningsHistory}
              deliveries={deliveries}
              weeklySummary={weeklySummary}
            />
          )}

          {currentTab === "prediction" && (
            <PredictionSection workerRef={workerRef} />
          )}

          {currentTab === "deliveries" && (
            <DeliveriesSection deliveries={deliveries} />
          )}

          {currentTab === "demand" && (
            <DemandSection />
          )}

          {currentTab === "platforms" && (
            <PlatformsSection
              summary={summary}
              deliveries={deliveries}
            />
          )}

          {currentTab === "recommendations" && (
            <RecommendationsSection workerRef={workerRef} />
          )}

          {currentTab === "expenses" && (
            <ExpensesSection
              expenses={expenses}
              summary={summary}
            />
          )}

          {currentTab === "imports" && (
            <ImportsSection />
          )}

          {currentTab === "models" && (
            <ModelsSection />
          )}

          {currentTab === "settings" && (
            <SettingsSection
              workerRef={workerRef}
              onRefreshData={loadData}
            />
          )}
        </main>
      </div>
    </div>
  );
}
