"use client";

import React, { useState } from "react";
import {
  Cloud,
  CloudDrizzle,
  CloudLightning,
  CloudRain,
  Compass,
  Locate,
  LocateFixed,
  LocateOff,
  MapPin,
  Radio,
  Sun,
  Wind,
} from "lucide-react";
import { useGeolocation, DeviceLocation } from "../hooks/useGeolocation";
import { useWeather } from "../hooks/useWeather";

interface LiveTelemetryBarProps {
  onLocationChange?: (loc: DeviceLocation | null) => void;
}

export const LiveTelemetryBar: React.FC<LiveTelemetryBarProps> = ({ onLocationChange }) => {
  const geo = useGeolocation();
  const [manualModalOpen, setManualModalOpen] = useState(false);
  const [manualLat, setManualLat] = useState("17.4483");
  const [manualLng, setManualLng] = useState("78.3915");

  // Pass location up when changed
  React.useEffect(() => {
    if (onLocationChange) {
      onLocationChange(geo.location);
    }
  }, [geo.location, onLocationChange]);

  // Use active coordinates for weather (or Hyderabad/Bangalore study default)
  const currentLat = geo.location ? geo.location.lat : 17.4483;
  const currentLng = geo.location ? geo.location.lng : 78.3915;
  const { weather, isLoading: weatherLoading } = useWeather(currentLat, currentLng);

  const getWeatherIcon = (isRain: boolean, code: number) => {
    if (code >= 95) return <CloudLightning className="w-4 h-4 text-amber-400" />;
    if (isRain) return <CloudRain className="w-4 h-4 text-cyan-400" />;
    if (code <= 1) return <Sun className="w-4 h-4 text-lime" />;
    return <Cloud className="w-4 h-4 text-content-secondary" />;
  };

  return (
    <div className="bg-surface-1 border border-hairline rounded-2xl p-3.5 mb-6 shadow-card flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
      {/* Geolocation Section */}
      <div className="flex items-center space-x-3 min-w-0">
        <div
          className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 border transition-all ${
            geo.isSharing
              ? "bg-cyan-950/40 border-cyan-400/40 text-cyan-400 shadow-inner"
              : "bg-surface-2 border-hairline text-content-muted"
          }`}
        >
          {geo.isSharing ? (
            <LocateFixed className="w-4 h-4 animate-pulse" />
          ) : (
            <Locate className="w-4 h-4" />
          )}
        </div>

        <div className="min-w-0">
          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold text-content-primary">
              {geo.isSharing ? "Device Telemetry Active" : "Device Telemetry"}
            </span>
            <span
              className={`text-[9px] font-mono px-1.5 py-0.5 rounded border uppercase tracking-wider font-bold ${
                geo.isSharing
                  ? "bg-cyan-950/60 text-cyan-400 border-cyan-400/30"
                  : "bg-surface-2 text-content-muted border-hairline"
              }`}
            >
              {geo.isSharing ? "REAL DEVICE DATA" : "STANDBY"}
            </span>
          </div>

          <div className="text-[11px] text-content-muted truncate mt-0.5 flex items-center space-x-1.5 font-mono">
            {geo.isSharing && geo.location ? (
              <>
                <span className="text-content-primary">
                  {geo.location.lat}°N, {geo.location.lng}°E
                </span>
                <span>•</span>
                <span className="text-cyan-400 font-sans">±{geo.location.accuracy}m accuracy</span>
              </>
            ) : geo.error ? (
              <span className="text-rose-400">{geo.error}</span>
            ) : (
              <span>Location sharing disabled. Click to enable real-time spatial context.</span>
            )}
          </div>
        </div>
      </div>

      {/* Action Buttons for Location */}
      <div className="flex items-center space-x-2 shrink-0">
        {geo.isSharing ? (
          <button
            onClick={geo.stopSharing}
            className="px-3 py-1.5 rounded-full bg-rose-950/30 border border-rose-500/40 text-rose-300 hover:bg-rose-900/40 text-xs font-medium flex items-center space-x-1.5 transition-colors"
          >
            <LocateOff className="w-3.5 h-3.5" />
            <span>Stop Sharing</span>
          </button>
        ) : (
          <div className="flex items-center space-x-2">
            <button
              onClick={geo.startSharing}
              disabled={geo.isLoading}
              className="px-3.5 py-1.5 rounded-full bg-surface-2 border border-lime/40 text-content-primary hover:text-lime hover:border-lime text-xs font-semibold flex items-center space-x-1.5 transition-all shadow-sm"
            >
              <Radio className="w-3.5 h-3.5 text-lime" />
              <span>{geo.isLoading ? "Locating..." : "Share Device Location"}</span>
            </button>
            <button
              onClick={() => setManualModalOpen(!manualModalOpen)}
              title="Manual Coordinates"
              className="px-2.5 py-1.5 rounded-full bg-surface-2 border border-hairline text-content-muted hover:text-content-primary text-xs"
            >
              <MapPin className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {/* Live Weather Widget Capsule */}
        <div className="hidden lg:flex items-center space-x-3 bg-surface-2/70 border border-hairline rounded-xl px-3 py-1.5 text-xs">
          <div className="flex items-center space-x-2">
            {weather ? getWeatherIcon(weather.isRainy, weather.weatherCode) : <Cloud className="w-4 h-4 text-lime" />}
            <div>
              <div className="flex items-center space-x-1.5">
                <span className="font-semibold text-content-primary">
                  {weather ? `${weather.temperatureC}°C` : "27°C"}
                </span>
                <span className="text-content-muted text-[10px]">
                  {weather ? weather.conditionText : "Clear"}
                </span>
              </div>
              <div className="text-[9px] text-content-muted font-mono flex items-center space-x-1">
                <span>{weather?.isRainy ? "🌧️ High Demand Surge" : "🌬️ Baseline Demand"}</span>
                <span>•</span>
                <span className="text-[8px] opacity-75">Open-Meteo CC BY 4.0</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Manual Coordinates Input Modal / Expand */}
      {manualModalOpen && (
        <div className="w-full pt-3 border-t border-hairline/60 flex items-center space-x-2">
          <span className="text-[11px] text-content-muted font-mono">Simulate GPS:</span>
          <input
            type="text"
            value={manualLat}
            onChange={(e) => setManualLat(e.target.value)}
            placeholder="Latitude (e.g. 17.4483)"
            className="bg-surface-2 border border-hairline rounded-lg px-2 py-1 text-xs text-content-primary w-28 font-mono"
          />
          <input
            type="text"
            value={manualLng}
            onChange={(e) => setManualLng(e.target.value)}
            placeholder="Longitude (e.g. 78.3915)"
            className="bg-surface-2 border border-hairline rounded-lg px-2 py-1 text-xs text-content-primary w-28 font-mono"
          />
          <button
            onClick={() => {
              const latNum = parseFloat(manualLat);
              const lngNum = parseFloat(manualLng);
              if (!isNaN(latNum) && !isNaN(lngNum)) {
                geo.setManualLocation(latNum, lngNum);
                setManualModalOpen(false);
              }
            }}
            className="px-3 py-1 bg-lime text-canvas font-bold text-xs rounded-lg hover:opacity-90"
          >
            Apply
          </button>
        </div>
      )}
    </div>
  );
};

