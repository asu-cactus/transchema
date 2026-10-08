import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_25/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_25/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_25/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

agg_df1 = df1.groupby("city").agg(
    fare=("fare", "mean"),
    ride_id_count=("ride_id", "count"),
    ride_id_nunique=("ride_id", "nunique")
).reset_index()

# According to the target schema, 'ride_id' column is float, we take the average count of ride_id? 
# The partial plan shows COUNT and COUNT DISTINCT on ride_id, but target schema has 'ride_id' as float.
# The best guess is to use the average count of ride_id (or sum?), but since target examples show large float values for ride_id,
# we interpret 'ride_id' column in target as the average count of ride_id (or sum) from source1.
# The partial plan has COUNT and COUNT DISTINCT, but target schema has only one ride_id column (float).
# We will use the average count of ride_id (ride_id_count) as ride_id column in target.

# Rename ride_id_count to ride_id to match target schema
agg_df1 = agg_df1.rename(columns={"ride_id_count": "ride_id"})

# Join with df0 on city to get driver_count
joined = pd.merge(df0[["city", "driver_count"]], agg_df1[["city", "fare", "ride_id"]], on="city", how="inner")

# Reorder columns to match target schema: ['city', 'fare', 'ride_id', 'driver_count']
result = joined[["city", "fare", "ride_id", "driver_count"]]

result.to_csv(target_path, index=False)