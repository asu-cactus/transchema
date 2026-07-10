import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_44/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_44/training_1.csv", index_col=0)

joined = pd.merge(df0, df1, on="city")

result = joined[["city", "fare", "ride_id"]].copy()
result["city"] = result["city"].astype(str)
result["fare"] = result["fare"].astype(float)
result["ride_id"] = result["ride_id"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_44/target_multisource_mcts.csv", index=False)