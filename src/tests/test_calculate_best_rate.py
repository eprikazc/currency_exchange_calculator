from decimal import Decimal

from src.best_rate_calculator import calculate_best_rate


def test_calculate_best_rate():
    data = [
        ["AUD", "USD", Decimal(0.78)],
        ["NZD", "USD", Decimal(0.69)],
    ]
    rate = calculate_best_rate("AUD", "NZD", data, 4)
    assert rate == Decimal("1.130")
