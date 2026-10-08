import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_72/training_0.csv", index_col=0)
df0 = df0.rename(columns={"click": "0"})
df0["condition"] = df0["condition"].astype(int)
df0["0"] = df0["0"].astype(int)
df0.to_csv("autopipeline-benchmarks/github-pipelines/length1_72/target_multisource_mcts.csv", index=False)