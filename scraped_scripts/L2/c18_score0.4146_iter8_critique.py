import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_18/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_18/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_18/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

merged = pd.merge(df0, df1, on="city", how="inner")

grouped = merged.groupby(["ride_id", "city"], as_index=False).agg({"fare": "mean"})

result = grouped[["city", "fare", "ride_id"]].copy()
result["fare"] = result["fare"].astype(float)
result["ride_id"] = result["ride_id"].astype(int)

result.to_csv(target_path, index=False)