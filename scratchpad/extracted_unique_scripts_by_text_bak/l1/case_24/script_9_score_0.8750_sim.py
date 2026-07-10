import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_24/training_0.csv", index_col=0)
result = df0.groupby("condition", as_index=False)["click"].sum()
result["condition"] = result["condition"].astype(int)
result["click"] = result["click"].astype(int)
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_24/target_multisource_mcts.csv", index=False)