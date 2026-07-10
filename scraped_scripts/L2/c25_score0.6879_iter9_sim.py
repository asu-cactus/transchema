import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_25/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_25/training_1.csv", index_col=0)

agg1 = df1.groupby(['city']).agg({'fare':'sum', 'ride_id':'min'}).reset_index()
agg0 = df0.groupby(['city', 'type']).agg({'driver_count':'count'}).reset_index()

# The partial plan says group by city and type on both sources, but df1 has no 'type' column.
# So we must join df1 with df0 on city to get 'type' for grouping.
# Instead, do a join first on city to get 'type' in df1, then group by city and type.

df1_with_type = pd.merge(df1, df0[['city', 'type']], on='city', how='inner')

grouped = df1_with_type.groupby(['city', 'type']).agg(
    fare_sum=('fare', 'sum'),
    ride_id_min=('ride_id', 'min'),
    driver_count_count=('type', 'count')  # count of driver_count from df0 is ambiguous, so count of type in merged df1_with_type
).reset_index()

# Now join grouped with df0 on city and type to get driver_count from df0
# But driver_count_count is count of rows in merged df1_with_type, not driver_count from df0
# The partial plan says COUNT(Source2_25_0.driver_count), so count of driver_count in df0 grouped by city and type
driver_count_count = df0.groupby(['city', 'type'])['driver_count'].count().reset_index(name='driver_count')

final = pd.merge(grouped, driver_count_count, on=['city', 'type'], how='inner')

# Select and rename columns to match target schema
result = final[['city', 'fare_sum', 'ride_id_min', 'driver_count']]
result.columns = ['city', 'fare', 'ride_id', 'driver_count']

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_25/target_multisource_mcts.csv", index=False)