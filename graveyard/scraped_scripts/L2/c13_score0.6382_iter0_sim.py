import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_13/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_13/training_1.csv", index_col=0)

result = df0.groupby("type", as_index=False)["driver_count"].sum()
result["type"] = result["type"].astype(str)
result["driver_count"] = result["driver_count"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_13/target_multisource_mcts.csv", index=False)