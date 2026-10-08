import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_51/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_51/training_1.csv", index_col=0)

# Aggregate Source3_51_0 by city to get average fare and ride count
df0_agg = df0.groupby('city', as_index=False).agg(
    fare=('fare', 'mean'),
    ride_id=('ride_id', 'count')
)

# Join aggregated df0 with df1 on city
df_merged = pd.merge(df1, df0_agg, on='city', how='inner')

# Group by city, driver_count, type to ensure uniqueness and aggregate again to match target
df_final = df_merged.groupby(['city', 'driver_count', 'type'], as_index=False).agg(
    **{
        'Average Fare': ('fare', 'mean'),
        'Ride Count': ('ride_id', 'count')
    }
)

# Cast columns to target types
df_final['city'] = df_final['city'].astype(str)
df_final['driver_count'] = df_final['driver_count'].astype('Int64')
df_final['type'] = df_final['type'].astype(str)
df_final['Average Fare'] = df_final['Average Fare'].astype(float)
df_final['Ride Count'] = df_final['Ride Count'].astype('Int64')

# Reorder columns to match target schema
df_final = df_final[['city', 'driver_count', 'type', 'Average Fare', 'Ride Count']]

# Write output
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length3_51/target_multisource_mcts.csv", index=False)