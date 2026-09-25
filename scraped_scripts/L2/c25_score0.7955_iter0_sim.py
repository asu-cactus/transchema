import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_25/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_25/training_1.csv"
output_path = "autopipeline-benchmarks/github-pipelines/length2_25/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

grouped = df1.groupby("city").agg({
    "fare": "mean",
    "ride_id": "mean"
}).reset_index()

joined = pd.merge(df0, grouped, on="city", how="inner")

result = joined[["city", "fare", "ride_id", "driver_count"]].copy()
result["fare"] = result["fare"].astype(float)
result["ride_id"] = result["ride_id"].astype(float)
result["driver_count"] = result["driver_count"].astype(int)

result.to_csv(output_path, index=False)