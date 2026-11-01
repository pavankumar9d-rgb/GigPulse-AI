"""Intelligent Opportunity Recommendation and Optimization Engine.

Implements multi-objective candidate ranking:
  Score = Net_Hourly_Paise - Risk_Weight * Uncertainty_Penalty - Travel_Hourly_Penalty

Enforces hard constraints (platforms, distance, minimum net rate, excluded zones),
transparent component explainability, abstention rules, and advisory disclaimer.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from gigpulse_core.db.schema import RecommendationRunModel
from gigpulse_core.ml.demand import forecast_zone_demand
from gigpulse_core.ml.earnings import predict_worker_earnings
from gigpulse_core.money import paise_to_rupees_str


# Estimated distance matrix between study area zones (in meters)
DEFAULT_ZONE_DISTANCES_M: Dict[str, Dict[str, int]] = {
    "zone_koramangala": {
        "zone_koramangala": 500,
        "zone_indiranagar": 5200,
        "zone_hsr": 3800,
        "zone_whitefield": 14500,
        "zone_central": 6100,
    },
    "zone_indiranagar": {
        "zone_koramangala": 5200,
        "zone_indiranagar": 500,
        "zone_hsr": 8200,
        "zone_whitefield": 11000,
        "zone_central": 4500,
    },
    "zone_hsr": {
        "zone_koramangala": 3800,
        "zone_indiranagar": 8200,
        "zone_hsr": 500,
        "zone_whitefield": 15200,
        "zone_central": 9200,
    },
    "zone_whitefield": {
        "zone_koramangala": 14500,
        "zone_indiranagar": 11000,
        "zone_hsr": 15200,
        "zone_whitefield": 500,
        "zone_central": 16000,
    },
    "zone_central": {
        "zone_koramangala": 6100,
        "zone_indiranagar": 4500,
        "zone_hsr": 9200,
        "zone_whitefield": 16000,
        "zone_central": 500,
    },
}

RISK_WEIGHT_MAP = {
    "risk_averse": 0.35,
    "balanced": 0.20,
    "risk_tolerant": 0.10,
}

# Fuel cost per km in paise (approx ₹3.50/km for 2-wheelers = 350 paise/km)
FUEL_COST_PAISE_PER_KM = 350


class RecommendationEngine:
    """Multi-objective ranking engine for gig delivery opportunities."""

    def __init__(self, scoring_version: str = "v1.0.0"):
        self.scoring_version = scoring_version

    def evaluate_candidates(
        self,
        session: Session,
        worker_ref: str,
        candidate_platforms: List[str],
        candidate_zones: List[str],
        start_at: datetime,
        end_at: datetime,
        current_zone_code: str = "zone_koramangala",
        min_net_earnings_paise_per_hour: int = 0,
        max_travel_distance_m: int = 15000,
        risk_tolerance: str = "balanced",
        excluded_platforms: Optional[List[str]] = None,
        excluded_zones: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Rank viable (platform, zone, time) options under worker constraints."""
        excluded_platforms = excluded_platforms or []
        excluded_zones = excluded_zones or []

        risk_weight = RISK_WEIGHT_MAP.get(risk_tolerance, 0.20)
        duration_hours = max(0.5, (end_at - start_at).total_seconds() / 3600.0)

        # 1. Filter viable platforms and zones
        valid_platforms = [p for p in candidate_platforms if p not in excluded_platforms]
        valid_zones = [z for z in candidate_zones if z not in excluded_zones]

        if not valid_platforms:
            valid_platforms = ["zomato", "swiggy", "zepto"]
        if not valid_zones:
            valid_zones = ["zone_koramangala", "zone_indiranagar", "zone_hsr"]

        # 2. Get demand forecasts for candidate zones
        demand_forecasts = forecast_zone_demand(
            session,
            zone_codes=valid_zones,
            forecast_from=start_at,
            steps=2,
            interval_minutes=30,
        )
        # Average demand point prediction per zone
        zone_demand_map: Dict[str, float] = {}
        for df_item in demand_forecasts:
            z = df_item["zone_code"]
            zone_demand_map[z] = zone_demand_map.get(z, 0.0) + (df_item["point_prediction"] / 2.0)

        candidates = []
        excluded_candidates = []

        for plat in valid_platforms:
            for zone in valid_zones:
                cand_id = f"{plat}_{zone}_{start_at.strftime('%H%M')}"

                # Calculate travel distance from current worker zone
                dist_m = DEFAULT_ZONE_DISTANCES_M.get(current_zone_code, {}).get(zone, 3000)
                if dist_m > max_travel_distance_m:
                    excluded_candidates.append({
                        "candidate_id": cand_id,
                        "platform_code": plat,
                        "zone_code": zone,
                        "reason": f"Travel distance ({dist_m/1000:.1f} km) exceeds maximum limit ({max_travel_distance_m/1000:.1f} km)",
                    })
                    continue

                # Predict earnings
                earnings_pred = predict_worker_earnings(
                    session=session,
                    worker_ref=worker_ref,
                    platform_code=plat,
                    zone_code=zone,
                    start_at=start_at,
                    end_at=end_at,
                )

                q50_rate = earnings_pred["q50_paise_per_hour"]
                q10_rate = earnings_pred["q10_paise_per_hour"]
                q90_rate = earnings_pred["q90_paise_per_hour"]

                if q50_rate < min_net_earnings_paise_per_hour:
                    excluded_candidates.append({
                        "candidate_id": cand_id,
                        "platform_code": plat,
                        "zone_code": zone,
                        "reason": f"Expected net earnings (₹{q50_rate/100:.2f}/hr) below minimum threshold (₹{min_net_earnings_paise_per_hour/100:.2f}/hr)",
                    })
                    continue

                # Calculate travel cost and hourly penalty
                dist_km = dist_m / 1000.0
                travel_cost_paise = int(round(dist_km * FUEL_COST_PAISE_PER_KM))
                travel_hourly_penalty = int(round(travel_cost_paise / duration_hours))

                # Calculate uncertainty penalty: (Q90 - Q10) * risk_weight
                uncertainty_span = max(0, q90_rate - q10_rate)
                uncertainty_penalty = int(round(uncertainty_span * risk_weight))

                # Composite utility score: Net - UncertaintyPenalty - TravelPenalty
                composite_score = int(round(q50_rate - uncertainty_penalty - travel_hourly_penalty))

                avg_demand = round(zone_demand_map.get(zone, 8.0), 1)
                demand_tier = "High" if avg_demand >= 10.0 else ("Moderate" if avg_demand >= 5.0 else "Low")

                # Generate explainability reasons
                reasons = [
                    f"Expected net earnings of ₹{q50_rate/100:.2f}/hr (Gross: ₹{earnings_pred['expected_gross_paise']/(100*duration_hours):.2f}/hr, Fuel/Expenses: ₹{earnings_pred['expected_expenses_paise']/(100*duration_hours):.2f}/hr).",
                    f"{demand_tier} predicted order activity ({avg_demand} deliveries/30min) in {zone}.",
                    f"Estimated one-way travel: {dist_km:.1f} km (transit fuel penalty: ₹{travel_cost_paise/100:.2f}).",
                    f"Uncertainty discount of ₹{uncertainty_penalty/100:.2f}/hr applied for {risk_tolerance} risk preference (80% confidence interval: ₹{q10_rate/100:.0f} - ₹{q90_rate/100:.0f}/hr).",
                ]

                candidates.append({
                    "candidate_id": cand_id,
                    "platform_code": plat,
                    "zone_code": zone,
                    "start_at": start_at.isoformat(),
                    "end_at": end_at.isoformat(),
                    "duration_hours": round(duration_hours, 2),
                    "composite_score": composite_score,
                    "expected_net_paise_per_hour": q50_rate,
                    "expected_net_inr_per_hour": round(q50_rate / 100.0, 2),
                    "q10_inr_per_hour": round(q10_rate / 100.0, 2),
                    "q90_inr_per_hour": round(q90_rate / 100.0, 2),
                    "expected_session_net_paise": earnings_pred["expected_net_paise"],
                    "expected_session_net_inr": earnings_pred["expected_net_inr"],
                    "expected_session_gross_paise": earnings_pred["expected_gross_paise"],
                    "expected_session_gross_inr": earnings_pred["expected_gross_inr"],
                    "travel_distance_m": dist_m,
                    "travel_cost_paise": travel_cost_paise,
                    "travel_cost_inr": round(travel_cost_paise / 100.0, 2),
                    "uncertainty_penalty_paise": uncertainty_penalty,
                    "uncertainty_penalty_inr": round(uncertainty_penalty / 100.0, 2),
                    "demand_estimate": avg_demand,
                    "demand_tier": demand_tier,
                    "reasons": reasons,
                    "data_quality": "synthetic",
                })

        # Sort candidates descending by composite score
        candidates.sort(key=lambda c: c["composite_score"], reverse=True)

        # Store run in database for audit and transparency
        rec_run = RecommendationRunModel(
            worker_ref=worker_ref,
            constraints_json=json.dumps({
                "min_net_earnings_paise_per_hour": min_net_earnings_paise_per_hour,
                "max_travel_distance_m": max_travel_distance_m,
                "risk_tolerance": risk_tolerance,
                "excluded_platforms": excluded_platforms,
                "excluded_zones": excluded_zones,
                "current_zone_code": current_zone_code,
            }),
            scoring_version=self.scoring_version,
            candidates_json=json.dumps(candidates[:10]),
            selected_candidate_id=candidates[0]["candidate_id"] if candidates else None,
        )
        session.add(rec_run)
        session.commit()

        return {
            "worker_ref": worker_ref,
            "scoring_version": self.scoring_version,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "time_window": {
                "start_at": start_at.isoformat(),
                "end_at": end_at.isoformat(),
                "duration_hours": round(duration_hours, 2),
            },
            "recommendation_run_id": rec_run.id,
            "total_evaluated": len(candidates) + len(excluded_candidates),
            "viable_count": len(candidates),
            "top_candidate": candidates[0] if candidates else None,
            "ranked_candidates": candidates,
            "excluded_candidates": excluded_candidates,
            "disclaimer": (
                "Recommendations are decision-support insights derived from historical and simulated patterns. "
                "GigPulse AI does not promise, warrant, or guarantee specific order dispatches or earnings."
            ),
        }


def generate_recommendations(
    session: Session,
    worker_ref: str,
    candidate_platforms: List[str],
    candidate_zones: List[str],
    start_at: datetime,
    end_at: datetime,
    current_zone_code: str = "zone_koramangala",
    min_net_earnings_paise_per_hour: int = 0,
    max_travel_distance_m: int = 15000,
    risk_tolerance: str = "balanced",
    excluded_platforms: Optional[List[str]] = None,
    excluded_zones: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Helper service function for generating ranked recommendations."""
    engine = RecommendationEngine()
    return engine.evaluate_candidates(
        session=session,
        worker_ref=worker_ref,
        candidate_platforms=candidate_platforms,
        candidate_zones=candidate_zones,
        start_at=start_at,
        end_at=end_at,
        current_zone_code=current_zone_code,
        min_net_earnings_paise_per_hour=min_net_earnings_paise_per_hour,
        max_travel_distance_m=max_travel_distance_m,
        risk_tolerance=risk_tolerance,
        excluded_platforms=excluded_platforms,
        excluded_zones=excluded_zones,
    )

