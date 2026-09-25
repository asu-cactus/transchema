import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_77/training_0.csv", index_col=0)
agg = df0.groupby("fac_type", as_index=False)["capacity"].max()
agg["capacity"] = agg["capacity"].astype(int)
agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_77/target_multisource_mcts.csv", index=False)