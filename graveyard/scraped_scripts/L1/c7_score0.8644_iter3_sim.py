import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_7/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_7/training_1.csv", index_col=0)

agg = df1.groupby(['city', 'date']).agg(
    fare=('fare', 'mean'),
    ride_id=('ride_id', 'count')
).reset_index()

driver_avg = df0.groupby(['city', 'type']).agg(
    driver_count=('driver_count', 'mean')
).reset_index()

# We need to join the aggregated df1 with df0 on city and type.
# But agg has no 'type' column, so we join agg with df0 on city first, then merge with driver_avg on city and type.

# Actually, the partial plan says group_by on city, date, and type, aggregating avg fare, count ride_id, avg driver_count.
# So we need to join df1 and df0 first on city to get type in the same dataframe, then group.

df_merged = pd.merge(df1, df0, on='city', how='inner')

grouped = df_merged.groupby(['city', 'date', 'type']).agg(
    fare=('fare', 'mean'),
    ride_id=('ride_id', 'count'),
    driver_count=('driver_count', 'mean')
).reset_index()

# Cast types to match target schema
grouped['driver_count'] = grouped['driver_count'].round().astype('Int64')
grouped['fare'] = grouped['fare'].astype(float)
grouped['ride_id'] = grouped['ride_id'].astype('Int64')
grouped['city'] = grouped['city'].astype(str)
grouped['type'] = grouped['type'].astype(str)
grouped['date'] = grouped['date'].astype(str)

grouped = grouped[['city', 'driver_count', 'type', 'date', 'fare', 'ride_id']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_7/target_multisource_mcts.csv", index=False)