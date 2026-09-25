import pandas as pd

# Read source files with index_col=0 as per instructions
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_11/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_11/training_1.csv", index_col=0)

# Aggregate Source1 by city: sum of fare, count of ride_id
df1_agg = df1.groupby('city', as_index=False).agg({
    'fare': 'sum',
    'ride_id': 'count'
})

# Aggregate Source0 by city: sum of driver_count
df0_agg = df0.groupby('city', as_index=False).agg({
    'driver_count': 'sum'
})

# Join aggregated tables on city
final_df = pd.merge(df1_agg, df0_agg, on='city', how='inner')

# Rename columns to match target schema exactly
final_df.rename(columns={'ride_id': 'ride_id'}, inplace=True)

# Cast columns to correct types
final_df['city'] = final_df['city'].astype(str)
final_df['fare'] = final_df['fare'].astype(float)
final_df['ride_id'] = final_df['ride_id'].astype(float)
final_df['driver_count'] = final_df['driver_count'].astype(int)

# Write output
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length2_11/target_multisource_mcts.csv", index=False)