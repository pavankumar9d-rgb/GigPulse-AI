"""GigPulse Core Domain Package.

Provides money arithmetic in integer paise, interval union mathematics,
Pydantic record models, derived metrics calculations, CSV validation,
and deterministic synthetic data generation.
"""

from gigpulse_core.enums import (
    DeliveryStatus,
    ExpenseCategory,
    SessionStatus,
    SourceType,
    TargetQuality,
    TargetType,
)
from gigpulse_core.intervals import (
    TimeInterval,
    calculate_unioned_duration_seconds,
    union_intervals,
)
from gigpulse_core.metrics import (
    calculate_active_time_seconds,
    calculate_earnings_per_online_hour_paise,
    calculate_gross_earnings_paise,
    calculate_net_earnings_paise,
    calculate_online_time_seconds,
    calculate_platform_gross_shares,
    calculate_total_expenses_paise,
)
from gigpulse_core.models import (
    DeliveryRecord,
    ExpenseRecord,
    WorkSessionRecord,
    ZoneDemandRecord,
)
from gigpulse_core.money import (
    paise_to_rupees_str,
    rupees_to_paise,
    validate_non_negative_paise,
)
from gigpulse_core.synthetic_generator import SyntheticDataGenerator
from gigpulse_core.validator import (
    ValidationReport,
    validate_csv_content,
)

__all__ = [
    "DeliveryStatus",
    "ExpenseCategory",
    "SessionStatus",
    "SourceType",
    "TargetQuality",
    "TargetType",
    "TimeInterval",
    "union_intervals",
    "calculate_unioned_duration_seconds",
    "DeliveryRecord",
    "ExpenseRecord",
    "WorkSessionRecord",
    "ZoneDemandRecord",
    "paise_to_rupees_str",
    "rupees_to_paise",
    "validate_non_negative_paise",
    "calculate_gross_earnings_paise",
    "calculate_total_expenses_paise",
    "calculate_net_earnings_paise",
    "calculate_online_time_seconds",
    "calculate_active_time_seconds",
    "calculate_earnings_per_online_hour_paise",
    "calculate_platform_gross_shares",
    "ValidationReport",
    "validate_csv_content",
    "SyntheticDataGenerator",
]

