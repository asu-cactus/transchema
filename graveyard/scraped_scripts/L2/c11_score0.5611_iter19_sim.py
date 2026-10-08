import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_11/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_11/training_1.csv"
output_path = "autopipeline-benchmarks/github-pipelines/length2_11/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

agg_source1 = df1.groupby("city", as_index=False).agg({
    "fare": "mean",
    "ride_id": "mean"
})

joined = pd.merge(agg_source1, df0[["city", "driver_count"]], on="city", how="inner")

result = pd.concat([joined, df1], ignore_index=True, sort=False)

result = result[["city", "fare", "ride_id", "driver_count"]]

result["fare"] = pd.to_numeric(result["fare"], errors="coerce")
result["ride_id"] = pd.to_numeric(result["ride_id"], errors="coerce")
result["driver_count"] = pd.to_numeric(result["driver_count"], errors="coerce").fillna(0).astype(int)

result.to_csv(output_path, index=False)