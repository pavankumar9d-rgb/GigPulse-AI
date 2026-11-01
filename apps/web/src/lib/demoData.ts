/**
 * Academic Research Baseline Fixture Data
 * Provides zero-failure fallback data when the cloud backend is cold, offline,
 * or accessed as a standalone static preview on Vercel.
 */

export const DEMO_SUMMARY = {
  worker_ref: "worker_w01",
  display_name: "Pavan Kumar (Rider W01)",
  analytics: {
    earnings: {
      gross_paise: 5420000,
      gross_formatted: "₹54,200.00",
      total_expenses_paise: 1029734,
      total_expenses_formatted: "₹10,297.34",
      net_paise: 4390266,
      net_formatted: "₹43,902.66",
    },
    time: {
      online_hours: 328.5,
      active_hours: 242.0,
      idle_seconds: 311400,
    },
    rates: {
      net_earnings_per_online_hour: 133.62,
      net_earnings_per_online_hour_formatted: "₹133.62",
    },
    counts: {
      deliveries: 420,
      sessions: 48,
    },
    platform_gross_shares: {
      swift_bite: 45.2,
      flash_drop: 38.6,
      hyper_courier: 16.2,
    },
  },
};

export const DEMO_WEEKLY_SUMMARY = {
  reference_date: "2026-11-01",
  timezone: "Asia/Kolkata",
  completed_window: {
    start_date: "2026-10-25",
    end_date: "2026-10-31",
  },
  totals: {
    completed_gross_paise: 711953,
    completed_gross_inr: "₹7,119.53",
    completed_net_paise: 577651,
    completed_net_inr: "₹5,776.51",
    completed_trips: 58,
  },
  completed_days: [
    { date: "2026-10-25", day_name: "Sun", gross_inr: "₹1,050.00", net_inr: "₹850.00", delivery_count: 8, is_peak: false },
    { date: "2026-10-26", day_name: "Mon", gross_inr: "₹880.00", net_inr: "₹710.00", delivery_count: 7, is_peak: false },
    { date: "2026-10-27", day_name: "Tue", gross_inr: "₹920.00", net_inr: "₹750.00", delivery_count: 8, is_peak: false },
    { date: "2026-10-28", day_name: "Wed", gross_inr: "₹1,120.00", net_inr: "₹910.00", delivery_count: 9, is_peak: false },
    { date: "2026-10-29", day_name: "Thu", gross_inr: "₹980.00", net_inr: "₹800.00", delivery_count: 8, is_peak: false },
    { date: "2026-10-30", day_name: "Fri", gross_inr: "₹1,420.00", net_inr: "₹1,180.00", delivery_count: 11, is_peak: true },
    { date: "2026-10-31", day_name: "Sat", gross_inr: "₹749.53", net_inr: "₹576.51", delivery_count: 7, is_peak: false },
  ],
  today_in_progress: {
    date: "2026-11-01",
    day_name: "Sun",
    gross_paise: 45447,
    gross_inr: "₹454.47",
    delivery_count: 5,
  },
};

export const DEMO_RECOMMENDATIONS = {
  top_candidate: {
    zone_code: "zone_koramangala",
    platform_code: "flash_drop",
    expected_net_paise_per_hour: 16500,
    composite_score: 0.94,
    explanation_text: "High dinner surge with 1.4x order multiplier across Koramangala commercial hub.",
  },
  ranked_recommendations: [
    {
      zone_code: "zone_koramangala",
      platform_code: "flash_drop",
      expected_net_paise_per_hour: 16500,
      composite_score: 0.94,
      explanation_text: "High dinner surge with 1.4x order multiplier across Koramangala commercial hub.",
    },
    {
      zone_code: "zone_indiranagar",
      platform_code: "swift_bite",
      expected_net_paise_per_hour: 14200,
      composite_score: 0.88,
      explanation_text: "Steady restaurant deliveries with low travel distances.",
    },
    {
      zone_code: "zone_hsr",
      platform_code: "hyper_courier",
      expected_net_paise_per_hour: 12800,
      composite_score: 0.81,
      explanation_text: "Fast turnaround e-commerce packages.",
    },
  ],
};

export const DEMO_DELIVERIES = [
  {
    id: "deliv_101",
    completed_at: "2026-11-01T19:40:00Z",
    platform_code: "flash_drop",
    pickup_zone_code: "zone_koramangala",
    dropoff_zone_code: "zone_indiranagar",
    distance_meters: 4200,
    base_payout_paise: 14500,
    incentive_paise: 3000,
    tip_paise: 2000,
    payout_paise: 19500,
  },
  {
    id: "deliv_102",
    completed_at: "2026-11-01T18:15:00Z",
    platform_code: "swift_bite",
    pickup_zone_code: "zone_hsr",
    dropoff_zone_code: "zone_koramangala",
    distance_meters: 3100,
    base_payout_paise: 12000,
    incentive_paise: 2000,
    tip_paise: 1500,
    payout_paise: 15500,
  },
  {
    id: "deliv_103",
    completed_at: "2026-11-01T16:50:00Z",
    platform_code: "hyper_courier",
    pickup_zone_code: "zone_whitefield",
    dropoff_zone_code: "zone_indiranagar",
    distance_meters: 6800,
    base_payout_paise: 18000,
    incentive_paise: 4000,
    tip_paise: 3000,
    payout_paise: 25000,
  },
  {
    id: "deliv_104",
    completed_at: "2026-11-01T15:20:00Z",
    platform_code: "flash_drop",
    pickup_zone_code: "zone_koramangala",
    dropoff_zone_code: "zone_hsr",
    distance_meters: 3500,
    base_payout_paise: 13000,
    incentive_paise: 2500,
    tip_paise: 1000,
    payout_paise: 16500,
  },
];

export const DEMO_EXPENSES = [
  {
    id: "exp_101",
    recorded_at: "2026-11-01T14:00:00Z",
    category: "fuel",
    amount_paise: 35000,
    notes: "Petrol refill at Indian Oil pump",
  },
  {
    id: "exp_102",
    recorded_at: "2026-10-30T10:00:00Z",
    category: "vehicle_maintenance",
    amount_paise: 25000,
    notes: "Chain lubrication and brake inspection",
  },
];

export const DEMO_EARNINGS_HISTORY = [
  { session_id: "s1", platform_code: "flash_drop", gross_paise: 84000, net_paise: 68000, started_at: "2026-10-25" },
  { session_id: "s2", platform_code: "swift_bite", gross_paise: 72000, net_paise: 59000, started_at: "2026-10-26" },
  { session_id: "s3", platform_code: "flash_drop", gross_paise: 91000, net_paise: 74000, started_at: "2026-10-27" },
  { session_id: "s4", platform_code: "hyper_courier", gross_paise: 65000, net_paise: 52000, started_at: "2026-10-28" },
  { session_id: "s5", platform_code: "swift_bite", gross_paise: 89000, net_paise: 72000, started_at: "2026-10-29" },
  { session_id: "s6", platform_code: "flash_drop", gross_paise: 115000, net_paise: 95000, started_at: "2026-10-30" },
  { session_id: "s7", platform_code: "flash_drop", gross_paise: 78000, net_paise: 63000, started_at: "2026-10-31" },
];
