import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_62/training_0.csv", index_col=0)
df0 = df0.rename(columns={"Text Date": "Month", "Water Use": "Water Use", "Power Use": "Power Use"})
df0 = df0[["Month", "Water Use", "Power Use"]]
df0["Water Use"] = df0["Water Use"].astype(float)
df0["Power Use"] = df0["Power Use"].astype(int)
df0.to_csv("autopipeline-benchmarks/github-pipelines/length1_62/target_multisource_mcts.csv", index=False)