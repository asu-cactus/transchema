import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_25/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_25/training_1.csv", index_col=0)

agg_fare = df1.groupby("city")["fare"].mean()
agg_ride_id = df1.groupby("city")["ride_id"].count()
agg_driver_count = df0.groupby("city")["driver_count"].sum()

result = pd.DataFrame({
    "city": agg_fare.index,
    "fare": agg_fare.values,
    "ride_id": agg_ride_id.values,
    "driver_count": agg_driver_count.reindex(agg_fare.index).fillna(0).astype(int).values
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_25/target_multisource_mcts.csv", index=False)