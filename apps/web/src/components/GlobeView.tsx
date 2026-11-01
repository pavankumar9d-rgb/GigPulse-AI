"use client";

import React, { useEffect, useRef, useState, useCallback } from "react";
import { Compass, Globe, Info, Layers, LocateFixed, Maximize2, RefreshCw, ZoomIn, ZoomOut } from "lucide-react";
import { STUDY_ZONES, STUDY_CITY_CENTROIDS, StudyZoneCoordinate } from "../lib/zoneCoordinates";
import { DeviceLocation } from "../hooks/useGeolocation";

interface ZoneDemandPoint extends StudyZoneCoordinate {
  demandIndex?: number; // 0.0 - 1.0
  orderCount?: number;
  surgeMultiplier?: number;
}

interface GlobeViewProps {
  deviceLocation?: DeviceLocation | null;
  selectedZoneCode?: string;
  onSelectZone?: (zoneCode: string) => void;
  className?: string;
}

export const GlobeView: React.FC<GlobeViewProps> = ({
  deviceLocation,
  selectedZoneCode,
  onSelectZone,
  className = "",
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mapInstanceRef = useRef<any>(null);

  const [activeCity, setActiveCity] = useState<"Hyderabad" | "Bangalore">("Hyderabad");
  const [useMapLibre, setUseMapLibre] = useState<boolean>(true);
  const [mapError, setMapError] = useState<string | null>(null);
  const [isRotating, setIsRotating] = useState<boolean>(false);
  const [hoveredZone, setHoveredZone] = useState<ZoneDemandPoint | null>(null);
  const [hoverPosition, setHoverPosition] = useState<{ x: number; y: number } | null>(null);

  // Canvas orthographic globe state for offline / fallback rendering
  const globeAngleRef = useRef<{ yaw: number; pitch: number }>({ yaw: 78.4, pitch: -17.4 });
  const isDraggingRef = useRef<boolean>(false);
  const lastMouseRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });

  // Compile zones with demand intensity
  const zones: ZoneDemandPoint[] = Object.values(STUDY_ZONES).map((z, idx) => ({
    ...z,
    demandIndex: [0.92, 0.88, 0.95, 0.74, 0.81, 0.65, 0.58, 0.42, 0.69, 0.77, 0.83, 0.55, 0.62, 0.49, 0.4][idx % 15],
    orderCount: [128, 114, 142, 88, 96, 68, 54, 42, 79, 85, 99, 52, 64, 46, 38][idx % 15],
    surgeMultiplier: [1.35, 1.25, 1.45, 1.15, 1.2, 1.05, 1.0, 1.0, 1.1, 1.15, 1.25, 1.0, 1.05, 1.0, 1.0][idx % 15],
  }));

  // Attempt MapLibre GL JS Initialization
  useEffect(() => {
    let isCancelled = false;

    async function initMapLibre() {
      if (!useMapLibre || !mapContainerRef.current) return;

      try {
        // Dynamically import maplibre-gl on client
        const maplibreModule = (await import("maplibre-gl")) as any;
        const maplibregl = maplibreModule.default || maplibreModule;
        // Dynamically insert CSS if not already present
        if (!document.getElementById("maplibre-css")) {
          const link = document.createElement("link");
          link.id = "maplibre-css";
          link.rel = "stylesheet";
          link.href = "https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css";
          document.head.appendChild(link);
        }

        const tileUrl =
          process.env.NEXT_PUBLIC_MAP_TILE_URL || "https://tile.openstreetmap.org/{z}/{x}/{y}.png";

        const map = new maplibregl.Map({
          container: mapContainerRef.current,
          style: {
            version: 8,
            sources: {
              "osm-tiles": {
                type: "raster",
                tiles: [tileUrl],
                tileSize: 256,
                attribution: "© OpenStreetMap contributors",
              },
            },
            layers: [
              {
                id: "osm-layer",
                type: "raster",
                source: "osm-tiles",
                minzoom: 0,
                maxzoom: 19,
                paint: {
                  "raster-brightness-max": 0.35,
                  "raster-contrast": 0.35,
                  "raster-saturation": -0.9,
                },
              },
            ],
          },
          center: [78.42, 17.41],
          zoom: 10.5,
          pitch: 35,
          bearing: -15,
        });

        // Add zone markers
        zones.forEach((zone) => {
          const el = document.createElement("div");
          el.className = "group relative cursor-pointer";
          const isHigh = (zone.demandIndex || 0) > 0.8;
          el.innerHTML = `
            <div class="w-4 h-4 rounded-full flex items-center justify-center transition-all ${
              isHigh ? "bg-lime text-canvas scale-110 shadow-lime-glow" : "bg-surface-raised border border-lime/50 text-lime"
            }">
              <div class="w-1.5 h-1.5 rounded-full bg-canvas"></div>
            </div>
          `;

          el.onclick = () => {
            if (onSelectZone) onSelectZone(zone.zoneCode);
          };

          new maplibregl.Marker({ element: el })
            .setLngLat([zone.lng, zone.lat])
            .addTo(map);
        });

        // Add real device marker if available
        if (deviceLocation) {
          const devEl = document.createElement("div");
          devEl.className = "relative flex items-center justify-center";
          devEl.innerHTML = `
            <div class="w-5 h-5 rounded-full bg-cyan-400/30 border border-cyan-400 animate-ping absolute"></div>
            <div class="w-3.5 h-3.5 rounded-full bg-cyan-400 border-2 border-canvas shadow-lg relative z-10"></div>
          `;
          new maplibregl.Marker({ element: devEl })
            .setLngLat([deviceLocation.lng, deviceLocation.lat])
            .addTo(map);
        }

        mapInstanceRef.current = map;
      } catch (err: any) {
        if (!isCancelled) {
          setMapError("MapLibre WebGL unavailable. Running fallback interactive 3D orthographic globe.");
          setUseMapLibre(false);
        }
      }
    }

    initMapLibre();

    return () => {
      isCancelled = true;
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, [useMapLibre, deviceLocation]);

  // Fallback Interactive Canvas 3D Orthographic Globe Renderer
  useEffect(() => {
    if (useMapLibre) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animId: number;

    const render = () => {
      const width = (canvas.width = canvas.parentElement?.clientWidth || 600);
      const height = (canvas.height = canvas.parentElement?.clientHeight || 400);
      const radius = Math.min(width, height) * 0.42;
      const cx = width / 2;
      const cy = height / 2;

      ctx.clearRect(0, 0, width, height);

      // Deep Space background
      ctx.fillStyle = "#080907";
      ctx.fillRect(0, 0, width, height);

      // Atmospheric outer aura
      const aura = ctx.createRadialGradient(cx, cy, radius * 0.9, cx, cy, radius * 1.25);
      aura.addColorStop(0, "rgba(215, 245, 47, 0.12)");
      aura.addColorStop(0.5, "rgba(215, 245, 47, 0.03)");
      aura.addColorStop(1, "rgba(8, 9, 7, 0)");
      ctx.fillStyle = aura;
      ctx.beginPath();
      ctx.arc(cx, cy, radius * 1.25, 0, Math.PI * 2);
      ctx.fill();

      // Earth Globe Body
      const globeGrad = ctx.createRadialGradient(cx - radius * 0.3, cy - radius * 0.3, radius * 0.1, cx, cy, radius);
      globeGrad.addColorStop(0, "#1A1D16");
      globeGrad.addColorStop(0.7, "#11130F");
      globeGrad.addColorStop(1, "#0B0C09");
      ctx.fillStyle = globeGrad;
      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.fill();

      // Globe Rim Edge
      ctx.strokeStyle = "rgba(215, 245, 47, 0.35)";
      ctx.lineWidth = 1.2;
      ctx.stroke();

      // Orthographic Projection Transform
      const { yaw, pitch } = globeAngleRef.current;
      const toRad = Math.PI / 180;
      const lambda0 = yaw * toRad;
      const phi0 = pitch * toRad;

      const project = (lat: number, lng: number) => {
        const phi = lat * toRad;
        const lambda = lng * toRad;

        const cosC = Math.sin(phi0) * Math.sin(phi) + Math.cos(phi0) * Math.cos(phi) * Math.cos(lambda - lambda0);
        if (cosC < 0) return null; // Behind globe horizon

        const x = cx + radius * Math.cos(phi) * Math.sin(lambda - lambda0);
        const y = cy - radius * (Math.cos(phi0) * Math.sin(phi) - Math.sin(phi0) * Math.cos(phi) * Math.cos(lambda - lambda0));
        return { x, y, visible: cosC >= 0, scale: Math.max(0.2, cosC) };
      };

      // Draw Latitude / Longitude Graticules
      ctx.strokeStyle = "rgba(255, 255, 255, 0.06)";
      ctx.lineWidth = 0.8;
      for (let lat = -60; lat <= 60; lat += 30) {
        ctx.beginPath();
        let started = false;
        for (let lng = -180; lng <= 180; lng += 5) {
          const pt = project(lat, lng);
          if (pt) {
            if (!started) {
              ctx.moveTo(pt.x, pt.y);
              started = true;
            } else {
              ctx.lineTo(pt.x, pt.y);
            }
          } else {
            started = false;
          }
        }
        ctx.stroke();
      }

      // Draw Longitude Meridians
      for (let lng = -180; lng < 180; lng += 45) {
        ctx.beginPath();
        let started = false;
        for (let lat = -80; lat <= 80; lat += 5) {
          const pt = project(lat, lng);
          if (pt) {
            if (!started) {
              ctx.moveTo(pt.x, pt.y);
              started = true;
            } else {
              ctx.lineTo(pt.x, pt.y);
            }
          } else {
            started = false;
          }
        }
        ctx.stroke();
      }

      // Draw Academic Study Zones
      zones.forEach((z) => {
        const pt = project(z.lat, z.lng);
        if (!pt) return;

        const isSelected = z.zoneCode === selectedZoneCode;
        const isHigh = (z.demandIndex || 0) > 0.8;

        // Pulsing Demand Halo
        ctx.beginPath();
        ctx.arc(pt.x, pt.y, (isSelected ? 10 : 6) * pt.scale, 0, Math.PI * 2);
        ctx.fillStyle = isSelected
          ? "rgba(215, 245, 47, 0.45)"
          : isHigh
          ? "rgba(215, 245, 47, 0.25)"
          : "rgba(255, 255, 255, 0.15)";
        ctx.fill();

        // Zone Point Core
        ctx.beginPath();
        ctx.arc(pt.x, pt.y, (isSelected ? 5 : 3.5) * pt.scale, 0, Math.PI * 2);
        ctx.fillStyle = isSelected || isHigh ? "#D7F52F" : "#A6B880";
        ctx.fill();
        ctx.strokeStyle = "#080907";
        ctx.lineWidth = 1;
        ctx.stroke();
      });

      // Draw Real Device Location Marker if active
      if (deviceLocation) {
        const devPt = project(deviceLocation.lat, deviceLocation.lng);
        if (devPt) {
          // Animated Cyan Radar Ring
          const pulse = (Date.now() % 1500) / 1500;
          ctx.beginPath();
          ctx.arc(devPt.x, devPt.y, (12 + pulse * 14) * devPt.scale, 0, Math.PI * 2);
          ctx.strokeStyle = `rgba(34, 211, 238, ${1 - pulse})`;
          ctx.lineWidth = 1.5;
          ctx.stroke();

          // Core Device Pin
          ctx.beginPath();
          ctx.arc(devPt.x, devPt.y, 5 * devPt.scale, 0, Math.PI * 2);
          ctx.fillStyle = "#22D3EE";
          ctx.fill();
          ctx.strokeStyle = "#FFFFFF";
          ctx.lineWidth = 1.5;
          ctx.stroke();
        }
      }

      if (isRotating) {
        globeAngleRef.current.yaw = (globeAngleRef.current.yaw + 0.15) % 360;
      }

      animId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animId);
    };
  }, [useMapLibre, isRotating, selectedZoneCode, deviceLocation]);

  // Handle Drag on Fallback Globe
  const handleMouseDown = (e: React.MouseEvent) => {
    isDraggingRef.current = true;
    lastMouseRef.current = { x: e.clientX, y: e.clientY };
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDraggingRef.current) return;
    const dx = e.clientX - lastMouseRef.current.x;
    const dy = e.clientY - lastMouseRef.current.y;
    lastMouseRef.current = { x: e.clientX, y: e.clientY };

    globeAngleRef.current.yaw = (globeAngleRef.current.yaw - dx * 0.5) % 360;
    globeAngleRef.current.pitch = Math.max(-80, Math.min(80, globeAngleRef.current.pitch + dy * 0.5));
  };

  const handleMouseUp = () => {
    isDraggingRef.current = false;
  };

  // Focus Navigation Controls
  const focusCity = (cityName: "Hyderabad" | "Bangalore") => {
    setActiveCity(cityName);
    const target = STUDY_CITY_CENTROIDS[cityName];
    if (mapInstanceRef.current) {
      mapInstanceRef.current.flyTo({
        center: [target.lng, target.lat],
        zoom: target.zoom,
        pitch: 45,
        bearing: 0,
        essential: true,
      });
    } else {
      globeAngleRef.current = { yaw: target.lng, pitch: -target.lat };
    }
  };

  const resetGlobalView = () => {
    if (mapInstanceRef.current) {
      mapInstanceRef.current.flyTo({
        center: [78.0, 20.0],
        zoom: 2.2,
        pitch: 15,
        bearing: 0,
        essential: true,
      });
    } else {
      globeAngleRef.current = { yaw: 78.4, pitch: -17.4 };
    }
  };

  return (
    <div className={`relative bg-surface-1 border border-hairline rounded-2xl overflow-hidden flex flex-col ${className}`}>
      {/* Globe Top Navigation Bar */}
      <div className="px-4 py-3 border-b border-hairline flex items-center justify-between z-10 bg-surface-1/90 backdrop-blur-md">
        <div className="flex items-center space-x-2.5">
          <div className="w-6 h-6 rounded-lg bg-surface-2 border border-hairline flex items-center justify-center text-lime">
            <Globe className="w-3.5 h-3.5" />
          </div>
          <div>
            <span className="text-xs font-semibold text-content-primary">
              Interactive 3D Spatial Globe
            </span>
            <div className="flex items-center space-x-1.5 text-[10px] text-content-muted">
              <span className="text-lime font-mono">15 Academic Clusters</span>
              <span>•</span>
              <span className="text-content-muted font-mono">
                {useMapLibre ? "MapLibre GL Vector Engine" : "Offline Dark Vector Sphere"}
              </span>
            </div>
          </div>
        </div>

        {/* Action Capsule */}
        <div className="flex items-center space-x-1.5">
          {/* City Cluster Switchers */}
          <div className="flex bg-surface-2 rounded-full p-0.5 border border-hairline text-[11px]">
            <button
              onClick={() => focusCity("Hyderabad")}
              className={`px-2.5 py-1 rounded-full font-medium transition-all ${
                activeCity === "Hyderabad" ? "bg-surface-raised text-lime shadow-inner" : "text-content-muted hover:text-content-primary"
              }`}
            >
              Hyderabad
            </button>
            <button
              onClick={() => focusCity("Bangalore")}
              className={`px-2.5 py-1 rounded-full font-medium transition-all ${
                activeCity === "Bangalore" ? "bg-surface-raised text-lime shadow-inner" : "text-content-muted hover:text-content-primary"
              }`}
            >
              Bangalore
            </button>
          </div>

          {/* Reset Global View */}
          <button
            onClick={resetGlobalView}
            title="Reset Global View"
            className="w-7 h-7 rounded-full bg-surface-2 border border-hairline hover:border-lime/40 text-content-secondary hover:text-lime flex items-center justify-center transition-colors"
          >
            <Compass className="w-3.5 h-3.5" />
          </button>

          {/* Auto Rotate Toggle */}
          <button
            onClick={() => setIsRotating(!isRotating)}
            title="Auto-Rotate Globe"
            className={`w-7 h-7 rounded-full border flex items-center justify-center transition-colors ${
              isRotating
                ? "bg-lime text-canvas border-lime shadow-lime-sm"
                : "bg-surface-2 border-hairline text-content-secondary hover:text-content-primary"
            }`}
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRotating ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {/* Main Globe Display Container */}
      <div className="relative flex-1 min-h-[340px] md:min-h-[400px] w-full bg-canvas overflow-hidden">
        {useMapLibre ? (
          <div ref={mapContainerRef} className="absolute inset-0 w-full h-full" />
        ) : (
          <canvas
            ref={canvasRef}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            className="w-full h-full cursor-grab active:cursor-grabbing block"
          />
        )}

        {/* Real Device Location Pill Badge (Top Left of Globe) */}
        {deviceLocation && (
          <div className="absolute top-3 left-3 bg-surface-raised/90 backdrop-blur-md border border-cyan-400/30 rounded-xl px-3 py-1.5 flex items-center space-x-2 shadow-lg z-20">
            <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
            <div>
              <div className="flex items-center space-x-1.5">
                <span className="text-[10px] font-bold text-cyan-400 tracking-wider">
                  REAL DEVICE LOCATION
                </span>
                <span className="text-[9px] text-content-muted font-mono">
                  (±{deviceLocation.accuracy}m)
                </span>
              </div>
              <div className="text-[10px] font-mono text-content-primary">
                {deviceLocation.lat.toFixed(4)}°N, {deviceLocation.lng.toFixed(4)}°E
              </div>
            </div>
          </div>
        )}

        {/* Academic Study Cluster Legend (Bottom Left) */}
        <div className="absolute bottom-3 left-3 bg-surface-1/90 backdrop-blur-md border border-hairline rounded-xl p-2.5 space-y-1.5 text-[10px] z-20 max-w-[220px]">
          <div className="font-semibold text-content-primary flex items-center space-x-1">
            <Layers className="w-3 h-3 text-lime" />
            <span>Research Study Mesh</span>
          </div>
          <div className="flex items-center justify-between text-content-muted">
            <div className="flex items-center space-x-1.5">
              <span className="w-2 h-2 rounded-full bg-lime shadow-lime-sm" />
              <span>Peak Demand (&gt;0.8)</span>
            </div>
            <span className="font-mono text-lime font-bold">Surge 1.3x</span>
          </div>
          <div className="flex items-center justify-between text-content-muted">
            <div className="flex items-center space-x-1.5">
              <span className="w-2 h-2 rounded-full bg-surface-raised border border-lime/40" />
              <span>Standard Baseline</span>
            </div>
            <span className="font-mono">1.0x</span>
          </div>
          <div className="pt-1 border-t border-hairline/60 text-[9px] text-content-muted font-mono leading-tight">
            *Cluster centroids are synthetic academic benchmarks.
          </div>
        </div>

        {/* Attribution / Mode Pill (Bottom Right) */}
        <div className="absolute bottom-2.5 right-3 text-[9px] font-mono text-content-muted z-20 flex items-center space-x-2 bg-surface-1/80 backdrop-blur-sm px-2 py-0.5 rounded-md border border-hairline/50">
          <a
            href="https://www.openstreetmap.org/copyright"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-lime transition-colors underline"
          >
            © OpenStreetMap
          </a>
          <span>•</span>
          <span>Zero-Cost Academic Tier</span>
        </div>
      </div>
    </div>
  );
};
