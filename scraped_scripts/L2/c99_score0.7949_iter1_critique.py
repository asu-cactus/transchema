import pandas as pd

src0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length2_99/training_0.csv', index_col=0)
src1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length2_99/training_1.csv', index_col=0)

# Join on city to combine driver_count info with rides
joined = src0.merge(src1[['city']], on='city', how='inner')

# Group by city and aggregate driver_count by max (driver_count is unique per city in src0)
result = joined.groupby('city', as_index=False)['driver_count'].max()

result.to_csv('autopipeline-benchmarks/github-pipelines/length2_99/target_multisource_mcts.csv', index=False)