import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_7/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_7/training_1.csv", index_col=0)

# Join on city
final = pd.merge(df0, df1, how='inner', on='city')

# Convert ride_id to integer (target schema expects integer)
final['ride_id'] = final['ride_id'].astype(int)

# Ensure driver_count is integer (already integer but enforce)
final['driver_count'] = final['driver_count'].astype(int)

# Ensure fare is float
final['fare'] = final['fare'].astype(float)

# Select columns in target schema order
final = final[['city', 'driver_count', 'type', 'date', 'fare', 'ride_id']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length1_7/target_multisource_mcts.csv", index=False)