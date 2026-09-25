import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_69/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_69/training_1.csv"
output_path = "autopipeline-benchmarks/github-pipelines/length2_69/target_multisource_mcts.csv"

source0 = pd.read_csv(source0_path, index_col=0)
source1 = pd.read_csv(source1_path, index_col=0)

# Join on city (inner join to keep only cities present in both)
joined = pd.merge(source0, source1[['city']], on='city', how='inner')

# Select only city and driver_count columns
result = joined[['city', 'driver_count']]

# Remove duplicates if any
result = result.drop_duplicates(subset=['city', 'driver_count'])

# Ensure correct types
result['city'] = result['city'].astype(str)
result['driver_count'] = result['driver_count'].astype(int)

result.to_csv(output_path, index=False)