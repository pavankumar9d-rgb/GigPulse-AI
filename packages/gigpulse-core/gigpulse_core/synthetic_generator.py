"""Deterministic Synthetic Data Generator for GigPulse AI.

Adheres strictly to data/SYNTHETIC_DATA_SPEC.md:
- 100% of rows flagged with source_type="synthetic" and target_quality="synthetic".
- Fully deterministic output governed by explicit random seed.
- Produces valid CSVs matching deliveries, work_sessions, expenses, and zone_demand templates.
- Generates dataset_manifest.json documenting assumptions, row counts, and synthetic=true.
"""

import csv
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from gigpulse_core.enums import (
    DeliveryStatus,
    ExpenseCategory,
    SessionStatus,
    SourceType,
    TargetQuality,
    TargetType,
)
from gigpulse_core.validator import TEMPLATE_HEADERS

GENERATOR_VERSION = "1.0.0"

# Fictional platforms (PRD / Synthetic Spec requirement: do not use real trademarks)
FICTIONAL_PLATFORMS = [
    {"code": "flash_drop", "name": "FlashDrop (Demo Food)"},
    {"code": "swift_bite", "name": "SwiftBite (Demo Grocery)"},
    {"code": "hyper_courier", "name": "HyperCourier (Demo Parcels)"},
]

# Fictional coarse zones in Hyderabad study area
FICTIONAL_ZONES = [
    f"HYD_ZONE_{i:02d}" for i in range(1, 16)
]

# High-density vs suburban zones
HIGH_DEMAND_ZONES = {"HYD_ZONE_01", "HYD_ZONE_02", "HYD_ZONE_03", "HYD_ZONE_04", "HYD_ZONE_05"}
LOW_DEMAND_ZONES = {"HYD_ZONE_12", "HYD_ZONE_13", "HYD_ZONE_14", "HYD_ZONE_15"}

FICTIONAL_WORKERS = ["worker_w01", "worker_w02", "worker_w03"]


class SyntheticDataGenerator:
    def __init__(self, seed: int = 42, start_date: datetime = None, num_weeks: int = 8):
        self.seed = seed
        self.rng = random.Random(seed)
        if start_date is None:
            # 8 weeks leading up to late October 2026
            self.start_date = datetime(2026, 9, 1, 0, 0, tzinfo=timezone.utc)
        else:
            self.start_date = start_date
        self.num_weeks = num_weeks
        self.end_date = self.start_date + timedelta(weeks=num_weeks)

    def generate_all(self, output_dir: Path) -> Dict[str, Any]:
        """Generate all 4 CSV datasets and the dataset_manifest.json."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        sessions = self._generate_work_sessions()
        deliveries = self._generate_deliveries(sessions)
        expenses = self._generate_expenses(sessions)
        zone_demand = self._generate_zone_demand()

        # Write CSVs
        self._write_csv(output_dir / "work_sessions.csv", "work_sessions", sessions)
        self._write_csv(output_dir / "deliveries.csv", "deliveries", deliveries)
        self._write_csv(output_dir / "expenses.csv", "expenses", expenses)
        self._write_csv(output_dir / "zone_demand.csv", "zone_demand", zone_demand)

        # Generate and write manifest
        manifest = {
            "project": "GigPulse AI",
            "generator_version": GENERATOR_VERSION,
            "seed": self.seed,
            "synthetic": True,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "time_range": {
                "start": self.start_date.isoformat(),
                "end": self.end_date.isoformat(),
                "weeks": self.num_weeks,
            },
            "counts": {
                "work_sessions": len(sessions),
                "deliveries": len(deliveries),
                "expenses": len(expenses),
                "zone_demand_observations": len(zone_demand),
            },
            "platforms": [p["code"] for p in FICTIONAL_PLATFORMS],
            "zones_count": len(FICTIONAL_ZONES),
            "workers": FICTIONAL_WORKERS,
            "assumptions": [
                "All rows strictly labelled with source_type='synthetic' and target_quality='synthetic'",
                "Lunch peak (12:00-14:30) and dinner peak (19:00-22:30) simulated",
                "Weekend volume uplift (approx 25-35%) applied",
                "Multi-app overlapping shifts simulated to exercise interval union logic",
                "Requested orders and observed deliveries generated separately to demonstrate target distinction",
                "No proprietary platform formulas or real personal identifiers used"
            ],
        }

        with open(output_dir / "dataset_manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        return manifest

    def _generate_work_sessions(self) -> List[Dict[str, Any]]:
        sessions = []
        days_total = self.num_weeks * 7

        for day_offset in range(days_total):
            current_day = self.start_date + timedelta(days=day_offset)
            is_weekend = current_day.weekday() >= 5

            for worker_ref in FICTIONAL_WORKERS:
                # 85% chance of working on a given day
                if self.rng.random() > 0.85:
                    continue

                # Lunch shift: e.g. 11:30 - 15:00
                lunch_start = current_day.replace(hour=11, minute=30) + timedelta(minutes=self.rng.randint(-30, 30))
                lunch_duration = timedelta(hours=self.rng.uniform(2.5, 3.5))
                lunch_end = lunch_start + lunch_duration

                primary_platform = self.rng.choice(FICTIONAL_PLATFORMS)["code"]
                sessions.append({
                    "worker_ref": worker_ref,
                    "platform_code": primary_platform,
                    "started_at": lunch_start.isoformat(),
                    "ended_at": lunch_end.isoformat(),
                    "status": SessionStatus.COMPLETED.value,
                    "source_type": SourceType.SYNTHETIC.value,
                    "timezone": "Asia/Kolkata",
                })

                # Overlapping multi-app session (35% probability during peak)
                if self.rng.random() < 0.35:
                    secondary_platform = [p["code"] for p in FICTIONAL_PLATFORMS if p["code"] != primary_platform][0]
                    sec_start = lunch_start + timedelta(minutes=self.rng.randint(15, 45))
                    sec_end = min(lunch_end, sec_start + timedelta(hours=self.rng.uniform(1.0, 2.5)))
                    sessions.append({
                        "worker_ref": worker_ref,
                        "platform_code": secondary_platform,
                        "started_at": sec_start.isoformat(),
                        "ended_at": sec_end.isoformat(),
                        "status": SessionStatus.COMPLETED.value,
                        "source_type": SourceType.SYNTHETIC.value,
                        "timezone": "Asia/Kolkata",
                    })

                # Dinner shift: e.g. 18:30 - 23:00
                dinner_start = current_day.replace(hour=18, minute=30) + timedelta(minutes=self.rng.randint(-30, 30))
                dinner_duration = timedelta(hours=self.rng.uniform(3.5, 4.5))
                dinner_end = dinner_start + dinner_duration

                dinner_platform = self.rng.choice(FICTIONAL_PLATFORMS)["code"]
                sessions.append({
                    "worker_ref": worker_ref,
                    "platform_code": dinner_platform,
                    "started_at": dinner_start.isoformat(),
                    "ended_at": dinner_end.isoformat(),
                    "status": SessionStatus.COMPLETED.value,
                    "source_type": SourceType.SYNTHETIC.value,
                    "timezone": "Asia/Kolkata",
                })

        return sessions

    def _generate_deliveries(self, sessions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        deliveries = []
        delivery_id = 1

        for s_idx, session in enumerate(sessions):
            s_start = datetime.fromisoformat(session["started_at"])
            s_end = datetime.fromisoformat(session["ended_at"])
            session_duration_hrs = (s_end - s_start).total_seconds() / 3600.0

            # 1 to 4 deliveries per hour during shift
            num_deliveries = max(0, int(round(session_duration_hrs * self.rng.uniform(1.2, 2.5))))
            if num_deliveries == 0:
                continue

            current_time = s_start + timedelta(minutes=self.rng.randint(5, 20))

            for _ in range(num_deliveries):
                if current_time >= s_end:
                    break

                pickup_zone = self.rng.choice(FICTIONAL_ZONES)
                drop_zone = self.rng.choice(FICTIONAL_ZONES)

                # Distance in meters (1.5 km to 9 km)
                distance_m = int(self.rng.uniform(1500, 9000))
                # Duration seconds (15 to 45 mins)
                duration_sec = int(self.rng.uniform(900, 2700))

                accepted_at = current_time
                completed_at = accepted_at + timedelta(seconds=duration_sec)

                if completed_at > s_end + timedelta(minutes=30):
                    # Delivery extended beyond shift end or shift cancelled
                    break

                # Payout in paise: Base ₹40-₹70 (4000-7000 paise) + ₹10/km (1000 paise/km)
                base_paise = self.rng.randint(4000, 7000)
                distance_paise = int((distance_m / 1000.0) * self.rng.randint(800, 1400))
                payout_paise = base_paise + distance_paise

                # Occasional incentive (20% probability, e.g. ₹20 - ₹50)
                incentive_paise = self.rng.randint(2000, 5000) if self.rng.random() < 0.20 else 0

                # Occasional tip (15% probability, e.g. ₹10 - ₹40)
                tip_paise = self.rng.randint(1000, 4000) if self.rng.random() < 0.15 else 0

                # Cancellation edge case (2% probability)
                is_cancelled = self.rng.random() < 0.02
                status = DeliveryStatus.CANCELLED.value if is_cancelled else DeliveryStatus.COMPLETED.value
                if is_cancelled:
                    payout_paise = int(payout_paise * 0.2)  # nominal cancellation compensation
                    incentive_paise = 0
                    tip_paise = 0

                deliveries.append({
                    "worker_ref": session["worker_ref"],
                    "platform_code": session["platform_code"],
                    "session_ref": f"sess_{s_idx:05d}",
                    "accepted_at": accepted_at.isoformat(),
                    "completed_at": completed_at.isoformat(),
                    "pickup_zone_code": pickup_zone,
                    "drop_zone_code": drop_zone,
                    "payout_paise": payout_paise,
                    "incentive_paise": incentive_paise,
                    "tip_paise": tip_paise,
                    "distance_m": distance_m,
                    "duration_seconds": duration_sec,
                    "status": status,
                    "target_quality": TargetQuality.SYNTHETIC.value,
                    "source_type": SourceType.SYNTHETIC.value,
                })

                delivery_id += 1
                current_time = completed_at + timedelta(minutes=self.rng.randint(5, 25))

        return deliveries

    def _generate_expenses(self, sessions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        expenses = []
        days_seen = set()

        for s_idx, session in enumerate(sessions):
            day_str = session["started_at"][:10]
            worker_ref = session["worker_ref"]
            key = (day_str, worker_ref)

            if key not in days_seen:
                days_seen.add(key)
                s_start = datetime.fromisoformat(session["started_at"])

                # Daily fuel or charging expense: ₹150 - ₹350 (15000 - 35000 paise)
                fuel_paise = self.rng.randint(15000, 35000)
                expenses.append({
                    "worker_ref": worker_ref,
                    "session_ref": f"sess_{s_idx:05d}",
                    "occurred_at": s_start.isoformat(),
                    "category": ExpenseCategory.FUEL.value if self.rng.random() < 0.8 else ExpenseCategory.CHARGING.value,
                    "amount_paise": fuel_paise,
                    "source_type": SourceType.SYNTHETIC.value,
                    "notes": "Daily vehicle replenishment (fictional)",
                })

                # Weekly mobile data recharge (approx once every 7 days)
                if self.rng.random() < 0.14:
                    expenses.append({
                        "worker_ref": worker_ref,
                        "session_ref": None,
                        "occurred_at": (s_start + timedelta(hours=1)).isoformat(),
                        "category": ExpenseCategory.MOBILE_DATA.value,
                        "amount_paise": self.rng.randint(25000, 45000),  # ₹250-₹450
                        "source_type": SourceType.SYNTHETIC.value,
                        "notes": "Weekly high-speed data top-up (fictional)",
                    })

                # Occasional maintenance/parking
                if self.rng.random() < 0.05:
                    expenses.append({
                        "worker_ref": worker_ref,
                        "session_ref": f"sess_{s_idx:05d}",
                        "occurred_at": (s_start + timedelta(hours=3)).isoformat(),
                        "category": ExpenseCategory.MAINTENANCE.value if self.rng.random() < 0.5 else ExpenseCategory.PARKING.value,
                        "amount_paise": self.rng.randint(5000, 15000),  # ₹50-₹150
                        "source_type": SourceType.SYNTHETIC.value,
                        "notes": "Routine vehicle upkeep/parking fee (fictional)",
                    })

        return expenses

    def _generate_zone_demand(self) -> List[Dict[str, Any]]:
        """Generate 30-minute interval observations across zones.
        
        Demonstrates the clear separation between requested orders, completed
        orders, observed deliveries, and demand proxies.
        """
        observations = []
        # Sample across selected days to keep dataset compact (first 14 days of the 8 weeks)
        sample_days = 14

        for day in range(sample_days):
            current_day = self.start_date + timedelta(days=day)
            is_weekend = current_day.weekday() >= 5
            weekend_multiplier = 1.35 if is_weekend else 1.0

            # 48 30-minute intervals per day
            for slot in range(48):
                interval_start = current_day + timedelta(minutes=slot * 30)
                hour = interval_start.hour

                # Hour curve: Lunch peak (12-14), Dinner peak (19-22), Night dip (01-06)
                if 12 <= hour <= 14:
                    hour_multiplier = 2.2
                elif 19 <= hour <= 22:
                    hour_multiplier = 2.8
                elif 1 <= hour <= 6:
                    hour_multiplier = 0.2
                else:
                    hour_multiplier = 1.0

                for zone in FICTIONAL_ZONES:
                    if zone in HIGH_DEMAND_ZONES:
                        zone_multiplier = 1.8
                    elif zone in LOW_DEMAND_ZONES:
                        zone_multiplier = 0.4
                    else:
                        zone_multiplier = 1.0

                    base_orders = 15.0 * hour_multiplier * zone_multiplier * weekend_multiplier
                    # Add Poisson-like noise
                    requested = max(0, int(round(self.rng.gauss(base_orders, max(2.0, base_orders * 0.25)))))
                    
                    # Completed is a fraction of requested (fulfillment rate 80-98%)
                    fulfillment_rate = self.rng.uniform(0.82, 0.98)
                    completed = min(requested, int(round(requested * fulfillment_rate)))

                    # Observed deliveries is only the worker sample (~5-15% of total orders)
                    deliveries_observed = max(0, int(round(completed * self.rng.uniform(0.05, 0.15))))

                    # Demand proxy value (e.g., composite demand intensity index)
                    proxy_val = round(base_orders * self.rng.uniform(0.9, 1.1), 2)

                    # Coverage fraction of sensor/rider presence
                    coverage = round(min(1.0, max(0.1, zone_multiplier * hour_multiplier * 0.35)), 2)

                    observations.append({
                        "zone_code": zone,
                        "interval_start": interval_start.isoformat(),
                        "interval_minutes": 30,
                        "orders_requested": requested,
                        "orders_completed": completed,
                        "deliveries_observed": deliveries_observed,
                        "demand_proxy_value": proxy_val,
                        "target_type": TargetType.REQUESTED_ORDERS.value,
                        "coverage_fraction": coverage,
                        "target_quality": TargetQuality.SYNTHETIC.value,
                        "source_type": SourceType.SYNTHETIC.value,
                    })

        return observations

    def _write_csv(self, file_path: Path, template_key: str, rows: List[Dict[str, Any]]):
        headers = TEMPLATE_HEADERS[template_key]
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for r in rows:
                writer.writerow(r)

