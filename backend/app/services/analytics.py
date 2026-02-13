from __future__ import annotations

from collections.abc import Sequence

import numpy as np


def calculate_percentile(current_value: float, history_values: Sequence[float]) -> float:
    if not history_values:
        return 50.0
    arr = np.array(history_values, dtype=float)
    arr = arr[~np.isnan(arr)]
    if arr.size == 0:
        return 50.0
    rank = np.searchsorted(np.sort(arr), float(current_value), side="right")
    return float(round((rank / arr.size) * 100, 2))


def get_temperature_status(percentile: float, low: float = 30, high: float = 70) -> str:
    if percentile < low:
        return "low"
    if percentile > high:
        return "high"
    return "medium"


def get_temperature_color(percentile: float, colors: dict[str, str], low: float = 30, high: float = 70) -> str:
    status = get_temperature_status(percentile, low=low, high=high)
    if status == "low":
        return colors.get("low", "#4CAF50")
    if status == "high":
        return colors.get("high", "#F44336")
    return colors.get("medium", "#FFC107")

