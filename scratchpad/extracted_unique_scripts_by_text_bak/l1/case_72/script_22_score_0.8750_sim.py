import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_72/training_0.csv", index_col=0)
agg = df0.groupby("condition", as_index=False)["click"].sum()
agg.columns = ["condition", "0"]
agg["condition"] = agg["condition"].astype(int)
agg["0"] = agg["0"].astype(int)
agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_72/target_multisource_mcts.csv", index=False)