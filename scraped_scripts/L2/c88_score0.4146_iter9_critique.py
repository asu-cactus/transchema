import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_88/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_88/training_1.csv", index_col=0)

# Join on city
df_joined = pd.merge(df1, df0[['city']], on='city', how='inner')

# Group by ride_id, aggregate fare by mean
grouped = df_joined.groupby('ride_id', as_index=False).agg({'fare': 'mean'})

# Add city back by joining on ride_id (ride_id is unique in df1)
# Since city is unique per ride_id in df1, we can get city by merging again
result = pd.merge(grouped, df1[['ride_id', 'city']], on='ride_id', how='left')

# Reorder columns to match target schema: city, fare, ride_id
result = result[['city', 'fare', 'ride_id']]

# Cast types
result['city'] = result['city'].astype(str)
result['fare'] = result['fare'].astype(float)
result['ride_id'] = result['ride_id'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_88/target_multisource_mcts.csv", index=False)