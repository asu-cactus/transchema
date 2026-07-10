import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_16/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_16/training_1.csv", index_col=0)

agg_df1 = df1.groupby("city").agg(
    ride_id=("ride_id", "count"),
    fare=("fare", "max")
).reset_index()

agg_df0 = df0.groupby("city").agg(
    driver_count=("driver_count", "sum")
).reset_index()

merged = pd.merge(agg_df0, agg_df1, on="city", how="inner")

merged = merged.astype({
    "city": str,
    "fare": float,
    "ride_id": float,
    "driver_count": int
})

merged.to_csv("autopipeline-benchmarks/github-pipelines/length2_16/target_multisource_mcts.csv", index=False)