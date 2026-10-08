import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_87/training_0.csv", index_col=0)
agg = df0.groupby("condition", as_index=False)["click"].sum()
agg["click"] = agg["click"].astype(float)
agg["condition"] = agg["condition"].astype(int)
agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_87/target_multisource_mcts.csv", index=False)