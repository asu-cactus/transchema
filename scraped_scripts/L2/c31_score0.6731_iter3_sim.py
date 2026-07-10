import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_31/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_31/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_31/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

merged = pd.merge(df0, df1, on="city", how="inner")

agg = merged.groupby(["type", "city"]).agg(
    fare=("fare", "mean"),
    ride_id=("ride_id", "count"),
    driver_count=("driver_count", "mean")
).reset_index()

agg["ride_id"] = agg["ride_id"].astype(float)
agg["driver_count"] = agg["driver_count"].round().astype("Int64")

agg.to_csv(target_path, index=False)