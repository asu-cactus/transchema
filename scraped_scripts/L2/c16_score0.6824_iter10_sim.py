import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_16/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_16/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_16/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

agg = df1.groupby("city").agg(
    ride_id=("ride_id", "count"),
    fare=("fare", "sum")
).reset_index()

joined = pd.merge(df0, agg, how="inner", on="city")

joined = joined[["city", "fare", "ride_id", "driver_count"]]

joined["fare"] = joined["fare"].astype(float)
joined["ride_id"] = joined["ride_id"].astype(float)
joined["driver_count"] = joined["driver_count"].astype(int)

joined.to_csv(target_path, index=False)