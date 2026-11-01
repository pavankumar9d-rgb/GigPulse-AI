"""Unit tests for money arithmetic in integer paise."""

import pytest
from gigpulse_core.money import (
    paise_to_rupees_str,
    rupees_to_paise,
    validate_non_negative_paise,
)


def test_paise_to_rupees_formatting():
    assert paise_to_rupees_str(0) == "₹0.00"
    assert paise_to_rupees_str(50) == "₹0.50"
    assert paise_to_rupees_str(100) == "₹1.00"
    assert paise_to_rupees_str(12550) == "₹125.50"
    assert paise_to_rupees_str(1000000) == "₹10000.00"
    assert paise_to_rupees_str(-4500) == "-₹45.00"


def test_rupees_to_paise_conversion():
    assert rupees_to_paise(0) == 0
    assert rupees_to_paise(125.50) == 12550
    assert rupees_to_paise("125.50") == 12550
    assert rupees_to_paise("₹125.50") == 12550
    assert rupees_to_paise("₹1,250.75") == 125075


def test_validate_non_negative_paise():
    assert validate_non_negative_paise(0) == 0
    assert validate_non_negative_paise(100) == 100

    with pytest.raises(ValueError, match="must be non-negative"):
        validate_non_negative_paise(-1)

    with pytest.raises(TypeError, match="must be an integer"):
        validate_non_negative_paise(50.5)  # type: ignore

