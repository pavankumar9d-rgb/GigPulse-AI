"use client";

import { useState, useEffect } from "react";

export interface LiveWeatherReport {
  temperatureC: number;
  humidityPct: number;
  precipitationMm: number;
  weatherCode: number;
  conditionText: string;
  windSpeedKmh: number;
  isRainy: boolean;
  demandImpactText: string;
  source: "OPEN_METEO_LIVE" | "CACHED" | "OFFLINE_ESTIMATED";
  fetchedAt: string;
  attribution: string;
}

const WEATHER_CODE_MAP: Record<number, { text: string; isRain: boolean }> = {
  0: { text: "Clear sky", isRain: false },
  1: { text: "Mainly clear", isRain: false },
  2: { text: "Partly cloudy", isRain: false },
  3: { text: "Overcast", isRain: false },
  45: { text: "Fog", isRain: false },
  48: { text: "Depositing rime fog", isRain: false },
  51: { text: "Light drizzle", isRain: true },
  53: { text: "Moderate drizzle", isRain: true },
  55: { text: "Dense drizzle", isRain: true },
  61: { text: "Slight rain", isRain: true },
  63: { text: "Moderate rain", isRain: true },
  65: { text: "Heavy rain", isRain: true },
  80: { text: "Rain showers", isRain: true },
  81: { text: "Heavy showers", isRain: true },
  82: { text: "Violent rain showers", isRain: true },
  95: { text: "Thunderstorm", isRain: true },
  96: { text: "Thunderstorm with slight hail", isRain: true },
  99: { text: "Thunderstorm with heavy hail", isRain: true },
};

const CACHE_TTL_MS = 10 * 60 * 1000; // 10 minutes cache
const cacheStore: Record<string, { data: LiveWeatherReport; expiry: number }> = {};

export function useWeather(lat: number = 17.4483, lng: number = 78.3915) {
  const [weather, setWeather] = useState<LiveWeatherReport | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    const cacheKey = `${lat.toFixed(2)}_${lng.toFixed(2)}`;

    const fetchWeather = async () => {
      // 1. Check in-memory cache
      const cached = cacheStore[cacheKey];
      if (cached && Date.now() < cached.expiry) {
        if (isMounted) {
          setWeather({ ...cached.data, source: "CACHED" });
          setIsLoading(false);
        }
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lng}&current=temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m`;
        const res = await fetch(url, { signal: AbortSignal.timeout(5000) });

        if (!res.ok) {
          throw new Error(`Open-Meteo returned status ${res.status}`);
        }

        const data = await res.json();
        const current = data.current;
        const code = current?.weather_code ?? 0;
        const meta = WEATHER_CODE_MAP[code] || { text: "Clear", isRain: false };

        const isRain = meta.isRain || (current?.precipitation ?? 0) > 0.1;
        const demandImpact = isRain
          ? "Rain Surge: +35-45% higher order demand & incentive multipliers"
          : "Favorable Weather: Standard baseline delivery demand and travel speeds";

        const report: LiveWeatherReport = {
          temperatureC: Math.round(current?.temperature_2m ?? 26),
          humidityPct: Math.round(current?.relative_humidity_2m ?? 65),
          precipitationMm: Number((current?.precipitation ?? 0).toFixed(1)),
          weatherCode: code,
          conditionText: meta.text,
          windSpeedKmh: Math.round(current?.wind_speed_10m ?? 12),
          isRainy: isRain,
          demandImpactText: demandImpact,
          source: "OPEN_METEO_LIVE",
          fetchedAt: new Date().toLocaleTimeString("en-IN", { timeZone: "Asia/Kolkata" }),
          attribution: "Weather data by Open-Meteo (CC BY 4.0)",
        };

        cacheStore[cacheKey] = {
          data: report,
          expiry: Date.now() + CACHE_TTL_MS,
        };

        if (isMounted) {
          setWeather(report);
          setIsLoading(false);
        }
      } catch (err: any) {
        // Fallback to estimated weather
        const fallback: LiveWeatherReport = {
          temperatureC: 27,
          humidityPct: 62,
          precipitationMm: 0.0,
          weatherCode: 1,
          conditionText: "Mainly clear (Est.)",
          windSpeedKmh: 14,
          isRainy: false,
          demandImpactText: "Baseline demand conditions (Offline estimation)",
          source: "OFFLINE_ESTIMATED",
          fetchedAt: new Date().toLocaleTimeString("en-IN", { timeZone: "Asia/Kolkata" }),
          attribution: "Weather data by Open-Meteo (CC BY 4.0)",
        };

        if (isMounted) {
          setWeather(fallback);
          setError("External weather API unreachable; using offline estimated baseline.");
          setIsLoading(false);
        }
      }
    };

    fetchWeather();

    return () => {
      isMounted = false;
    };
  }, [lat, lng]);

  return { weather, isLoading, error };
}

