import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_11/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_11/training_1.csv", index_col=0)

agg1 = pd.merge(
    df1.groupby('city', as_index=False).agg({'fare':'sum', 'ride_id':'count'}),
    df0.groupby('city', as_index=False).agg({'driver_count':'count'}),
    on='city',
    how='inner'
)

agg1.rename(columns={'ride_id':'ride_id_count'}, inplace=True)

# The partial plan suggests grouping by city and type first, but type only exists in df0.
# We do a groupby on city and type on df0 and city on df1, then join on city and type.
# However, df1 has no 'type' column, so we must join df0 and df1 on city first, then group.

# Step 1: group df0 by city and type with count of driver_count
df0_agg = df0.groupby(['city', 'type'], as_index=False).agg({'driver_count':'count'})

# Step 2: group df1 by city with sum of fare and count of ride_id
df1_agg = df1.groupby('city', as_index=False).agg({'fare':'sum', 'ride_id':'count'})

# Step 3: join df0_agg and df1_agg on city (type only in df0_agg)
join_df = pd.merge(df0_agg, df1_agg, on='city', how='inner')

# Step 4: group by city again to aggregate final columns as per target schema
final_agg = join_df.groupby('city', as_index=False).agg({
    'fare':'sum',
    'ride_id':'sum',
    'driver_count':'sum'
})

# Rename columns to match target schema
final_agg.rename(columns={'ride_id':'ride_id', 'driver_count':'driver_count'}, inplace=True)

# Ensure correct dtypes
final_agg['city'] = final_agg['city'].astype(str)
final_agg['fare'] = final_agg['fare'].astype(float)
final_agg['ride_id'] = final_agg['ride_id'].astype(float)
final_agg['driver_count'] = final_agg['driver_count'].astype(int)

final_agg.to_csv("autopipeline-benchmarks/github-pipelines/length2_11/target_multisource_mcts.csv", index=False)