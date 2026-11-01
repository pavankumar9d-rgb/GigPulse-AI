/**
 * Zone Geographic Centroids for Academic Study Clusters.
 * 
 * DISCLAIMER:
 * These coordinates represent approximate study cluster centroids for
 * academic spatial demand modeling and research simulations.
 * They are clearly tagged as SYNTHETIC RESEARCH DATA / APPROXIMATE CLUSTERS
 * and NEVER represent real worker real-time GPS locations without consent.
 */

export interface StudyZoneCoordinate {
  zoneCode: string;
  displayName: string;
  city: "Hyderabad" | "Bangalore";
  lat: number;
  lng: number;
  clusterRadiusMeters: number;
  syntheticTag: "SYNTHETIC RESEARCH DATA";
}

export const STUDY_ZONES: Record<string, StudyZoneCoordinate> = {
  // Hyderabad Study Area Cluster (15 research zones)
  HYD_ZONE_01: {
    zoneCode: "HYD_ZONE_01",
    displayName: "Madhapur IT Hub",
    city: "Hyderabad",
    lat: 17.4483,
    lng: 78.3915,
    clusterRadiusMeters: 2500,
    syntheticTag: "SYNTHETIC RESEARCH DATA",
  },
  HYD_ZONE_02: {
    zoneCode: "HYD_ZONE_02",
    displayName: "Gachibowli Financial",
    city: "Hyderabad",
    lat: 17.4401,
    lng: 78.3489,
    clusterRadiusMeters: 3000,
    syntheticTag: "SYNTHETIC RESEARCH DATA",
  },
  HYD_ZONE_03: {
    zoneCode: "HYD_ZONE_03",
    displayName: "Hitec City Core",
    city: "Hyderabad",
    lat: 17.4504,
    lng: 78.3808,
    clusterRadiusMeters: 2200,
    syntheticTag: "SYNTHETIC RESEARCH DATA",
  },
  HYD_ZONE_04: {
    zoneCode: "HYD_ZONE_04",
    displayName: "Kondapur Residential",
    city: "Hyderabad",
    lat: 17.4699,
    lng: 78.3578,
    clusterRadiusMeters: 2400,
    syntheticTag: "SYNTHETIC RESEARCH DATA",
  },
  HYD_ZONE_05: {
    zoneCode: "HYD_ZONE_05",
    displayName: "Jubilee Hills Central",
    city: "Hyderabad",
    lat: 17.4319,
    lng: 78.4073,
    clusterRadiusMeters: 2800,
    syntheticTag: "SYNTHETIC RESEARCH DATA",
  },
  HYD_ZONE_06: {
    zoneCode: "HYD_ZONE_06",
    displayName: "Banjara Hills Rd 12",
    city: "Hyderabad",
    lat: 17.4156,
    lng: 78.435,
    clusterRadiusMeters: 2600,
    syntheticTag: "SYNTHETIC RESEARCH DATA",
  },
  HYD_ZONE_07: {
    zoneCode: "HYD_ZONE_07",
    displayName: "Kukatpally Housing Board",
    city: "Hyderabad",
    lat: 17.4933,
    lng: 78.3914,
    clusterRadiusMeters: 3200,
    syntheticTag: "SYNTHETIC RESEARCH DATA",
  },
  HYD_ZONE_08: {
    zoneCode: "HYD_ZONE_08",
    displayName: "Miyapur Metro Corridor",
    city: "Hyderabad",
    lat: 17.4968,
    lng: 78.3548,
    clusterRadiusMeters: 3100,
    syntheticTag: "SYNTHETIC RESEARCH DATA",
  },
  HYD_ZONE_09: {
    zoneCode: "HYD_ZONE_09",
    displayName: "Begumpet Commercial",
    city: "Hyderabad",
    lat: 17.4447,
    lng: 78.4664,
    clusterRadiusMeters: 2500,
    syntheticTag: "SYNTHETIC RESEARCH DATA",
  },
  HYD_ZONE_10: {
    zoneCode: "HYD_ZONE_10",
    displayName: "Ameerpet Metro Hub",
    city: "Hyderabad",
    lat: 17.4375,
    lng: 78.4482,
    clusterRadiusMeters: 2000,
    syntheticTag: "SYNTHETIC RESEARCH DATA",
  },
  HYD_ZONE_11: {
    zoneCode: "HYD_ZONE_11",
    displayName: "Somajiguda Medical Center",
    city: "Hyderabad",
    lat: 17.4262,
    lng: 78.4601,
    clusterRadiusMeters: 2100,
    syntheticTag: "SYNTHETIC RESEARCH DATA",
  },
  HYD_ZONE_12: {
    zoneCode: "HYD_ZONE_12",
    displayName: "Secunderabad Station",
    city: "Hyderabad",
    lat: 17.4399,
    lng: 78.4983,
    clusterRadiusMeters: 3400,
    syntheticTag: "SYNTHETIC RESEARCH DATA",
  },
  HYD_ZONE_13: {
    zoneCode: "HYD_ZONE_13",
    displayName: "Mehdipatnam Transit",
    city: "Hyderabad",
    lat: 17.3916,
    lng: 78.4414,
    clusterRadiusMeters: 2900,
    syntheticTag: "SYNTHETIC RESEARCH DATA",
  },
  HYD_ZONE_14: {
    zoneCode: "HYD_ZONE_14",
    displayName: "Dilsukhnagar Market",
    city: "Hyderabad",
    lat: 17.3688,
    lng: 78.5247,
    clusterRadiusMeters: 3300,
    syntheticTag: "SYNTHETIC RESEARCH DATA",
  },
  HYD_ZONE_15: {
    zoneCode: "HYD_ZONE_15",
    displayName: "Charminar Old City",
    city: "Hyderabad",
    lat: 17.3616,
    lng: 78.4747,
    clusterRadiusMeters: 2700,
    syntheticTag: "SYNTHETIC RESEARCH DATA",
  },

  // Bangalore Study Area Mesh
  zone_koramangala: {
    zoneCode: "zone_koramangala",
    displayName: "Koramangala 5th Block",
    city: "Bangalore",
    lat: 12.9352,
    lng: 77.6245,
    clusterRadiusMeters: 2400,
    syntheticTag: "SYNTHETIC RESEARCH DATA",
  },
  zone_indiranagar: {
    zoneCode: "zone_indiranagar",
    displayName: "Indiranagar 100ft Rd",
    city: "Bangalore",
    lat: 12.9784,
    lng: 77.6408,
    clusterRadiusMeters: 2200,
    syntheticTag: "SYNTHETIC RESEARCH DATA",
  },
  zone_hsr: {
    zoneCode: "zone_hsr",
    displayName: "HSR Sector 1 & 2",
    city: "Bangalore",
    lat: 12.9121,
    lng: 77.6446,
    clusterRadiusMeters: 2600,
    syntheticTag: "SYNTHETIC RESEARCH DATA",
  },
  zone_whitefield: {
    zoneCode: "zone_whitefield",
    displayName: "Whitefield EPIP Zone",
    city: "Bangalore",
    lat: 12.9698,
    lng: 77.7499,
    clusterRadiusMeters: 3500,
    syntheticTag: "SYNTHETIC RESEARCH DATA",
  },
  zone_jayanagar: {
    zoneCode: "zone_jayanagar",
    displayName: "Jayanagar 4th Block",
    city: "Bangalore",
    lat: 12.9308,
    lng: 77.5838,
    clusterRadiusMeters: 2800,
    syntheticTag: "SYNTHETIC RESEARCH DATA",
  },
};

export const STUDY_CITY_CENTROIDS = {
  Hyderabad: { lat: 17.41, lng: 78.42, zoom: 11 },
  Bangalore: { lat: 12.96, lng: 77.64, zoom: 11 },
  Global: { lat: 20.0, lng: 78.0, zoom: 2 },
};

