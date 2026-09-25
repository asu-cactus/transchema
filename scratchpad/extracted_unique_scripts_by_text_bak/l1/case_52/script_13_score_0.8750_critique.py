import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_52/training_0.csv", index_col=0)
df0["condition"] = df0["condition"].astype(int)
df0["click"] = df0["click"].astype(int)

result = df0.groupby("condition").agg({"click": lambda x: (x == 0).sum()}).reset_index()
result.columns = ["condition", "0"]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_52/target_multisource_mcts.csv", index=False)