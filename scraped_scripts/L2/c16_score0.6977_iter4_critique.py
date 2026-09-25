import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_16/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_16/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_16/target_multisource_mcts.csv"

# Read sources with index_col=0 to ignore the first numerical index column
df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Join on city (inner join to keep only cities present in both)
joined = pd.merge(df0, df1, on='city', how='inner')

# Group by city
grouped = joined.groupby('city', as_index=False).agg({
    'fare': 'mean',          # average fare per city
    'ride_id': 'count',      # count of rides per city
    'driver_count': 'first'  # driver_count per city from df0 (same for all rows per city)
})

# Rename columns to match target schema exactly
grouped = grouped.rename(columns={'ride_id': 'ride_id'})

# Ensure correct types
grouped['city'] = grouped['city'].astype(str)
grouped['fare'] = grouped['fare'].astype(float)
grouped['ride_id'] = grouped['ride_id'].astype(float)  # count as float to match target schema
grouped['driver_count'] = grouped['driver_count'].astype(int)

# Select columns in target schema order
result = grouped[['city', 'fare', 'ride_id', 'driver_count']]

# Write to target path
result.to_csv(target_path, index=False)