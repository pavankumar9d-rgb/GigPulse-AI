/**
 * Typed API Client for GigPulse AI backend.
 * Provides automatic port fallback (8000 -> 8001) for local execution resilience.
 */

const PRIMARY_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";
const FALLBACK_URL = "http://127.0.0.1:8001/api/v1";
let activeBaseUrl = PRIMARY_URL;

async function fetchJson<T>(path: string, options?: RequestInit): Promise<T> {
  const tryFetch = async (baseUrl: string) => {
    const url = `${baseUrl}${path.startsWith("/") ? path : `/${path}`}`;
    const res = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options?.headers || {}),
      },
    });

    if (!res.ok) {
      let errMessage = `HTTP error ${res.status}`;
      try {
        const errData = await res.json();
        if (errData.error?.message) {
          errMessage = errData.error.message;
        }
      } catch {
        // ignore
      }
      throw new Error(errMessage);
    }

    activeBaseUrl = baseUrl;
    return res.json();
  };

  try {
    return await tryFetch(activeBaseUrl);
  } catch (err: any) {
    if (activeBaseUrl === PRIMARY_URL && PRIMARY_URL.includes("8000")) {
      try {
        return await tryFetch(FALLBACK_URL);
      } catch {
        throw err;
      }
    }
    throw err;
  }
}

export const api = {
  // Health
  getHealth: () => fetchJson<{ status: string; database_status: string; synthetic_mode: boolean }>("/health"),

  // Workers
  getWorkers: () => fetchJson<{ items: Array<{ id: string; worker_ref: string; display_name: string }> }>("/workers"),

  // Dashboard & Analytics
  getDashboardSummary: (workerRef?: string, startDate?: string, endDate?: string) => {
    const params = new URLSearchParams();
    if (workerRef) params.append("worker_ref", workerRef);
    if (startDate) params.append("start_date", startDate);
    if (endDate) params.append("end_date", endDate);
    return fetchJson<any>(`/dashboard/summary?${params.toString()}`);
  },

  getWeeklyEarnings: (workerRef?: string, referenceDate?: string) => {
    const params = new URLSearchParams();
    if (workerRef) params.append("worker_ref", workerRef);
    if (referenceDate) params.append("reference_date", referenceDate);
    return fetchJson<any>(`/earnings/weekly-summary?${params.toString()}`);
  },

  getEarningsHistory: (workerRef?: string, platformCode?: string, limit = 50) => {
    const params = new URLSearchParams();
    if (workerRef) params.append("worker_ref", workerRef);
    if (platformCode) params.append("platform_code", platformCode);
    params.append("limit", limit.toString());
    return fetchJson<any>(`/earnings/history?${params.toString()}`);
  },

  // Platforms & Zones
  getPlatforms: () => fetchJson<{ items: Array<{ id: string; code: string; display_name: string; active: boolean }> }>("/platforms"),
  getZones: () => fetchJson<{ items: Array<{ id: string; zone_code: string; display_name: string }> }>("/zones"),

  // Deliveries & Expenses
  getDeliveries: (workerRef?: string, limit = 50) => {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (workerRef) params.append("worker_ref", workerRef);
    return fetchJson<any>(`/deliveries?${params.toString()}`);
  },

  getExpenses: (workerRef?: string, limit = 50) => {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (workerRef) params.append("worker_ref", workerRef);
    return fetchJson<any>(`/expenses?${params.toString()}`);
  },

  getWorkSessions: (workerRef?: string, limit = 50) => {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (workerRef) params.append("worker_ref", workerRef);
    return fetchJson<any>(`/sessions?${params.toString()}`);
  },

  // Machine Learning: Earnings Prediction
  predictEarnings: (data: {
    worker_ref: string;
    platform_code: string;
    zone_code: string;
    start_at: string;
    end_at: string;
    prediction_unit?: string;
    include_interval?: boolean;
  }) => fetchJson<any>("/forecasts/earnings", {
    method: "POST",
    body: JSON.stringify(data),
  }),

  // Machine Learning: Zone Demand Forecast
  forecastDemand: (data: {
    zone_codes: string[];
    forecast_from: string;
    steps?: number;
    interval_minutes?: number;
    target_type?: string;
  }) => fetchJson<any>("/forecasts/demand", {
    method: "POST",
    body: JSON.stringify(data),
  }),

  // Optimization: Opportunity Recommendation
  getRecommendations: (data: {
    worker_ref: string;
    candidate_zone_ids: string[];
    candidate_platform_ids: string[];
    time_window: { start_at: string; end_at: string };
    preferences?: any;
  }) => fetchJson<any>("/recommendations/preview", {
    method: "POST",
    body: JSON.stringify(data),
  }),

  // Models Registry
  getModels: () => fetchJson<{ models: any[] }>("/models"),
  getModelDetails: (id: string) => fetchJson<any>(`/models/${id}`),
  retrainModels: () => fetchJson<any>("/models/train", { method: "POST" }),

  // Data Imports
  validateImport: (fileContent: string, templateType: string, filename: string) => {
    return fetchJson<any>("/imports/validate", {
      method: "POST",
      body: JSON.stringify({
        raw_csv_content: fileContent,
        template_type: templateType,
        filename: filename,
      }),
    });
  },

  commitImport: (batchId: string) => fetchJson<any>(`/imports/${batchId}/commit`, { method: "POST" }),

  // Governance
  exportData: (workerRef: string) => fetchJson<any>(`/data/export?worker_ref=${workerRef}`, { method: "POST" }),
  deleteAccountData: (workerRef: string) => fetchJson<any>(`/account/data?worker_ref=${workerRef}&confirm=true`, { method: "DELETE" }),
};
