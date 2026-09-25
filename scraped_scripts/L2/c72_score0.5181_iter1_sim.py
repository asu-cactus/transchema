import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_72/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_72/training_1.csv", index_col=0)

df = pd.merge(df0, df1, on="city")

result = df[["type", "fare", "ride_id", "driver_count"]].copy()
result["type"] = result["type"].astype(str)
result["fare"] = result["fare"].astype(float)
result["ride_id"] = result["ride_id"].astype(int)
result["driver_count"] = result["driver_count"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_72/target_multisource_mcts.csv", index=False)