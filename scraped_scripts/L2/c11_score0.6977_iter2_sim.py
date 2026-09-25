import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_11/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_11/training_1.csv", index_col=0)

agg1 = df1.groupby("city").agg(fare=("fare", "mean"), ride_id=("ride_id", "count")).reset_index()

joined = pd.merge(df0, agg1, on="city", how="inner")

final_agg = joined.groupby("city").agg(
    driver_count=("driver_count", "sum"),
    fare=("fare", "mean"),
    ride_id=("ride_id", "sum")
).reset_index()

final_agg["driver_count"] = final_agg["driver_count"].astype(int)
final_agg["fare"] = final_agg["fare"].astype(float)
final_agg["ride_id"] = final_agg["ride_id"].astype(float)

final_agg.to_csv("autopipeline-benchmarks/github-pipelines/length2_11/target_multisource_mcts.csv", index=False)