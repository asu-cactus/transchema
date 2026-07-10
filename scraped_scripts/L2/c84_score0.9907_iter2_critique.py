import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_84/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_84/training_1.csv", index_col=0)

# Join on city
merged = pd.merge(source0[['city', 'type']], source1[['city', 'ride_id']], on='city', how='inner')

# Group by type and count ride_id
result = merged.groupby('type', as_index=False).agg({'ride_id': 'count'})

# Select the row with the maximum ride_id count
result = result.loc[result['ride_id'].idxmax()]

# Convert the single row Series back to DataFrame with one row
result = pd.DataFrame([result])

# Write output with exact target schema and column names
result.to_csv("autopipeline-benchmarks/github-pipelines/length2_84/target_multisource_mcts.csv", index=False)