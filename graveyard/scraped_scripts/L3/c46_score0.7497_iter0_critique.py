import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_46/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_46/training_1.csv", index_col=0)

# Join on city
merged = pd.merge(df0, df1, on='city', how='inner')

# Group by city, driver_count, type and aggregate fare and ride_id
agg = merged.groupby(['city', 'driver_count', 'type']).agg(
    Average_Fare=('fare', 'mean'),
    Ride_Count=('ride_id', 'count')
).reset_index()

# Rename columns to match target schema exactly
agg.rename(columns={'Average_Fare': 'Average Fare', 'Ride_Count': 'Ride Count'}, inplace=True)

# Reorder columns as per target schema
result = agg[['city', 'driver_count', 'type', 'Average Fare', 'Ride Count']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_46/target_multisource_mcts.csv", index=False)