"use client";

import { useState, useEffect, useRef, useCallback } from "react";

export interface DeviceLocation {
  lat: number;
  lng: number;
  accuracy: number; // in meters
  timestamp: number;
  source: "REAL_BROWSER_GPS" | "MANUAL_OVERRIDE";
}

export interface GeolocationState {
  isSupported: boolean;
  isSharing: boolean;
  isLoading: boolean;
  location: DeviceLocation | null;
  error: string | null;
  startSharing: () => void;
  stopSharing: () => void;
  setManualLocation: (lat: number, lng: number) => void;
  clearManualLocation: () => void;
}

export function useGeolocation(): GeolocationState {
  const [isSupported, setIsSupported] = useState<boolean>(true);
  const [isSharing, setIsSharing] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [location, setLocation] = useState<DeviceLocation | null>(null);
  const [error, setError] = useState<string | null>(null);

  const watchIdRef = useRef<number | null>(null);

  useEffect(() => {
    if (typeof window !== "undefined") {
      setIsSupported("geolocation" in navigator);
    }
  }, []);

  const stopSharing = useCallback(() => {
    if (watchIdRef.current !== null && typeof window !== "undefined") {
      navigator.geolocation.clearWatch(watchIdRef.current);
      watchIdRef.current = null;
    }
    setIsSharing(false);
    setIsLoading(false);
    setLocation(null);
    setError(null);
  }, []);

  const startSharing = useCallback(() => {
    if (typeof window === "undefined" || !("geolocation" in navigator)) {
      setError("Geolocation is not supported by your browser.");
      return;
    }

    setIsLoading(true);
    setError(null);

    // Initial single acquisition
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLocation({
          lat: Number(pos.coords.latitude.toFixed(6)),
          lng: Number(pos.coords.longitude.toFixed(6)),
          accuracy: Math.round(pos.coords.accuracy),
          timestamp: pos.timestamp,
          source: "REAL_BROWSER_GPS",
        });
        setIsSharing(true);
        setIsLoading(false);

        // Continuous watch
        if (watchIdRef.current === null) {
          watchIdRef.current = navigator.geolocation.watchPosition(
            (updatedPos) => {
              setLocation({
                lat: Number(updatedPos.coords.latitude.toFixed(6)),
                lng: Number(updatedPos.coords.longitude.toFixed(6)),
                accuracy: Math.round(updatedPos.coords.accuracy),
                timestamp: updatedPos.timestamp,
                source: "REAL_BROWSER_GPS",
              });
            },
            (err) => {
              // Non-fatal watch error
              console.warn("Geolocation watch warning:", err.message);
            },
            {
              enableHighAccuracy: true,
              maximumAge: 10000,
              timeout: 20000,
            }
          );
        }
      },
      (err) => {
        setIsLoading(false);
        setIsSharing(false);
        switch (err.code) {
          case err.PERMISSION_DENIED:
            setError("Location permission denied by user. You can manually select a study zone.");
            break;
          case err.POSITION_UNAVAILABLE:
            setError("Device position unavailable. Please check GPS or connection.");
            break;
          case err.TIMEOUT:
            setError("Location request timed out. Please try again.");
            break;
          default:
            setError(err.message || "Unable to acquire location.");
        }
      },
      {
        enableHighAccuracy: true,
        timeout: 15000,
        maximumAge: 0,
      }
    );
  }, []);

  const setManualLocation = useCallback((lat: number, lng: number) => {
    stopSharing();
    setLocation({
      lat: Number(lat.toFixed(6)),
      lng: Number(lng.toFixed(6)),
      accuracy: 50,
      timestamp: Date.now(),
      source: "MANUAL_OVERRIDE",
    });
    setIsSharing(true);
    setError(null);
  }, [stopSharing]);

  const clearManualLocation = useCallback(() => {
    stopSharing();
  }, [stopSharing]);

  // Clean up watch on unmount
  useEffect(() => {
    return () => {
      if (watchIdRef.current !== null && typeof window !== "undefined") {
        navigator.geolocation.clearWatch(watchIdRef.current);
      }
    };
  }, []);

  return {
    isSupported,
    isSharing,
    isLoading,
    location,
    error,
    startSharing,
    stopSharing,
    setManualLocation,
    clearManualLocation,
  };
}

