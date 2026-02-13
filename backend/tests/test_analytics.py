from app.services.analytics import calculate_percentile, get_temperature_status


def test_calculate_percentile_empty():
    assert calculate_percentile(10, []) == 50.0


def test_calculate_percentile_normal():
    percentile = calculate_percentile(3, [1, 2, 3, 4, 5])
    assert 50.0 <= percentile <= 70.0


def test_temperature_status():
    assert get_temperature_status(20, low=30, high=70) == "low"
    assert get_temperature_status(50, low=30, high=70) == "medium"
    assert get_temperature_status(90, low=30, high=70) == "high"

