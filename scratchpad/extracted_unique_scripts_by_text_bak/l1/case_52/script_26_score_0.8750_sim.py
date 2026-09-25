import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_52/training_0.csv", index_col=0)
agg = df0.groupby("condition", as_index=False)["click"].max()
agg.rename(columns={"click": "0"}, inplace=True)
agg["condition"] = agg["condition"].astype(int)
agg["0"] = agg["0"].astype(int)
agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_52/target_multisource_mcts.csv", index=False)