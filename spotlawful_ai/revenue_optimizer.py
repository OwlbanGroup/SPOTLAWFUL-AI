from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any


class RevenueOptimizer:
    def __init__(self, data: Any):
        self.data = data

    def optimize_revenue(self):
        # Use a lightweight trend-based forecast that does not require third-party libraries.
        return self.calculate_optimized_revenue()

    def _extract_revenue_values(self) -> list[float]:
        if hasattr(self.data, "columns") and hasattr(self.data, "__getitem__"):
            if "revenue" not in self.data.columns:
                raise ValueError("Data must contain 'revenue' column")
            raw_values = self.data["revenue"]
        elif isinstance(self.data, Sequence) and not isinstance(self.data, (str, bytes)):
            try:
                raw_values = [row["revenue"] for row in self.data]
            except (TypeError, KeyError):
                raise ValueError("Data must be a DataFrame-like object or a sequence of records containing 'revenue'")
        else:
            raise TypeError("Data must be a DataFrame-like object or a sequence of records containing 'revenue'")

        values = [float(value) for value in raw_values]
        if not values:
            raise ValueError("Data must contain at least one revenue value")
        return values

    def calculate_optimized_revenue(self):
        y = self._extract_revenue_values()

        if len(y) == 1:
            predicted_revenue = y[0]
        else:
            x = list(range(len(y)))
            x_mean = sum(x) / len(x)
            y_mean = sum(y) / len(y)
            numerator = sum((x_value - x_mean) * (y_value - y_mean) for x_value, y_value in zip(x, y))
            denominator = sum((x_value - x_mean) ** 2 for x_value in x)
            slope = numerator / denominator if denominator else 0.0
            intercept = y_mean - (slope * x_mean)
            next_period = float(len(y))
            predicted_revenue = (slope * next_period) + intercept

        # Calculate optimized revenue as predicted revenue plus 10% uplift
        return predicted_revenue * 1.10

    def generate_report(self):
        optimized_revenue = self.optimize_revenue()
        return {
            "optimized_revenue": optimized_revenue,
            "details": "Revenue forecasted using lightweight trend analysis with 10% uplift.",
        }
