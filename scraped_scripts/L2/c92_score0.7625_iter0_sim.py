import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_92/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_92/training_1.csv", index_col=0)

joined = pd.merge(df0, df1, on="city", how="inner")

result = joined.groupby("type", as_index=False).agg({"ride_id": "count"})
result["ride_id"] = result["ride_id"].astype(int)
result["type"] = result["type"].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_92/target_multisource_mcts.csv", index=False)