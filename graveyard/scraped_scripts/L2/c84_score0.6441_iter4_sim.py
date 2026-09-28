import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_84/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_84/training_1.csv", index_col=0)

agg_df1 = df1.groupby("ride_id").agg(
    date_min=pd.NamedAgg(column="date", aggfunc="min"),
    date_max=pd.NamedAgg(column="date", aggfunc="max"),
    fare_avg=pd.NamedAgg(column="fare", aggfunc="mean")
).reset_index()

# Join on ride_id and type? The partial plan suggests group_by on ride_id and aggregations on df1,
# but df0 has no ride_id column, only city, driver_count, type.
# The only common column is city, but target schema is type and ride_id.
# The example target has type and ride_id.
# So we must join df0 and agg_df1 on city to get type for each ride_id.

# Join df1 with df0 on city to get type for each ride_id
df1_with_type = pd.merge(df1, df0[['city', 'type']], on='city', how='inner')

# Now group by ride_id and type to get unique pairs
result = df1_with_type[['type', 'ride_id']].drop_duplicates()

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_84/target_multisource_mcts.csv", index=False)