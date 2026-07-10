import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_60/training_0.csv", index_col=0)
result = df0.groupby("type", as_index=False)["driver_count"].sum()
result["driver_count"] = result["driver_count"].astype(int)
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_60/target_multisource_mcts.csv", index=False)