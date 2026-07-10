import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_88/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_88/training_1.csv", index_col=0)

merged = pd.merge(df1, df0, on="city", how="inner")

result = merged[["city", "fare", "ride_id"]].copy()
result["fare"] = result["fare"].astype(float)
result["ride_id"] = result["ride_id"].astype(int)
result["city"] = result["city"].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_88/target_multisource_mcts.csv", index=False)