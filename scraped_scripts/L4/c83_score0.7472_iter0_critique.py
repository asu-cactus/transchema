import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_1.csv", index_col=0)

# Step 1: Group Source0 by city to get average fare
grouped_fare = df0.groupby('city', as_index=False)['fare'].mean().rename(columns={'fare': 'average_fare'})

# Step 2: Join Source1 with grouped Source0 on city
merged = pd.merge(df1, grouped_fare, how='inner', on='city')

# Step 3: Group by city, driver_count, type to remove duplicates and aggregate average_fare
final = merged.groupby(['city', 'driver_count', 'type'], as_index=False)['average_fare'].mean()

# Ensure correct types
final['city'] = final['city'].astype(str)
final['driver_count'] = final['driver_count'].astype(int)
final['type'] = final['type'].astype(str)
final['average_fare'] = final['average_fare'].astype(float)

final = final[['city', 'driver_count', 'type', 'average_fare']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_83/target_multisource_mcts.csv", index=False)