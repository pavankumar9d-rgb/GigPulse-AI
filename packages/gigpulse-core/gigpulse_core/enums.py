"""Domain enumerations for GigPulse AI.

Maintains strict separation between target types, data provenance, and status.
"""

from enum import Enum


class SessionStatus(str, Enum):
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    CANCELLED = "cancelled"


class DeliveryStatus(str, Enum):
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


class ExpenseCategory(str, Enum):
    FUEL = "fuel"
    CHARGING = "charging"
    MAINTENANCE = "maintenance"
    PARKING = "parking"
    MOBILE_DATA = "mobile_data"
    OTHER = "other"


class TargetType(str, Enum):
    """Critical: never conflate these four demand targets."""
    REQUESTED_ORDERS = "requested_orders"
    COMPLETED_ORDERS = "completed_orders"
    OBSERVED_DELIVERIES = "observed_deliveries"
    DEMAND_PROXY = "proxy"


class TargetQuality(str, Enum):
    VERIFIED_AGGREGATE = "verified_aggregate"
    VERIFIED = "verified"
    USER_REPORTED = "user_reported"
    PROXY = "proxy"
    SYNTHETIC = "synthetic"


class SourceType(str, Enum):
    MANUAL = "manual"
    CSV_IMPORT = "csv_import"
    SYNTHETIC = "synthetic"
    AUTHORIZED_API = "authorized_api"

