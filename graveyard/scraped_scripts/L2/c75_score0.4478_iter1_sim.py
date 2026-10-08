import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_75/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_75/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="city", how="inner")

result = merged[["city", "ride_id"]].copy()
result["ride_id"] = result["ride_id"].astype("Int64")

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_75/target_multisource_mcts.csv", index=False)