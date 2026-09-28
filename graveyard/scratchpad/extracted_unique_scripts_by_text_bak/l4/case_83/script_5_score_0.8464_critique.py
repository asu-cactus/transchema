import pandas as pd

# Read source files
Source4_83_0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_0.csv", index_col=0)
Source4_83_1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_1.csv", index_col=0)

# Group Source4_83_0 by city to compute average fare
grouped_Source4_83_0 = Source4_83_0.groupby('city', as_index=False).agg(
    average_fare=('fare', 'mean')
)

# Join Source4_83_1 with aggregated fare data on city
result = pd.merge(Source4_83_1, grouped_Source4_83_0, on='city', how='inner')

# Select columns as per target schema
result = result[['city', 'driver_count', 'type', 'average_fare']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_83/target_multisource_mcts.csv", index=False)