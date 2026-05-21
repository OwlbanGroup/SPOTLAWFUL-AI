from spotlawful_ai.revenue_optimizer import RevenueOptimizer


def test_optimize_revenue_with_record_sequence():
    data = [
        {"revenue": 1000},
        {"revenue": 1500},
        {"revenue": 2000},
        {"revenue": 2500},
        {"revenue": 3000},
    ]

    optimizer = RevenueOptimizer(data)

    optimized_revenue = optimizer.optimize_revenue()

    assert optimized_revenue > 0
    assert round(optimized_revenue, 2) == 3850.0


if __name__ == "__main__":
    result = test_optimize_revenue_with_record_sequence()
    print("Revenue optimizer test passed.")
