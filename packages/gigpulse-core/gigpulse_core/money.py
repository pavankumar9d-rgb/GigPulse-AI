"""Monetary arithmetic in 64-bit integer paise (INR).

Authoritative money arithmetic is strictly integer-based to eliminate binary
floating-point rounding inaccuracies.
"""

from typing import Union


def paise_to_rupees_str(paise: int) -> str:
    """Format integer paise to standard Indian Rupee string, e.g. 15050 -> '₹150.50'."""
    sign = "-" if paise < 0 else ""
    abs_paise = abs(paise)
    rupees = abs_paise // 100
    remainder = abs_paise % 100
    return f"{sign}₹{rupees}.{remainder:02d}"


def rupees_to_paise(rupees: Union[int, float, str]) -> int:
    """Convert rupee value or string to integer paise.
    
    Rounds to nearest whole paisa to avoid floating-point drift.
    """
    if isinstance(rupees, str):
        cleaned = rupees.replace("₹", "").replace(",", "").strip()
        val = float(cleaned)
    else:
        val = float(rupees)
    return round(val * 100)


def validate_non_negative_paise(paise: int, field_name: str = "amount") -> int:
    """Ensure monetary value is non-negative."""
    if not isinstance(paise, int):
        raise TypeError(f"{field_name} must be an integer, got {type(paise).__name__}")
    if paise < 0:
        raise ValueError(f"{field_name} must be non-negative, got {paise}")
    return paise

