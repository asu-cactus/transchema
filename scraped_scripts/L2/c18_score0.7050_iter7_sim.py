import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_18/training_0.csv", index_col=0)

agg = df0.groupby("city").agg(
    fare_min=pd.NamedAgg(column="fare", aggfunc="min"),
    fare_max=pd.NamedAgg(column="fare", aggfunc="max"),
    ride_id_min=pd.NamedAgg(column="ride_id", aggfunc="min"),
)

agg = agg.reset_index()

# The target schema is ['city': string, 'fare': float, 'ride_id': integer]
# The partial plan suggests aggregating min and max fare, but target has only one fare column.
# We choose to take the average of min and max fare to produce a single fare value.
agg["fare"] = (agg["fare_min"] + agg["fare_max"]) / 2
agg["ride_id"] = agg["ride_id_min"].astype(int)

result = agg[["city", "fare", "ride_id"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_18/target_multisource_mcts.csv", index=False)