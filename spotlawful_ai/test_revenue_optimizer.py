import pandas as pd
from revenue_optimizer import RevenueOptimizer

# Sample data for testing
data = {
    'revenue': [1000, 1500, 2000, 2500, 3000]
}
df = pd.DataFrame(data)

# Create an instance of RevenueOptimizer
optimizer = RevenueOptimizer(df)

# Run the optimization
optimized_revenue = optimizer.optimize_revenue()

# Print the results
print("Optimized Revenue:", optimized_revenue)
