import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_46/training_0.csv", index_col=0)

df0 = df0.rename(columns={"Text Date": "Date", "Water Use": "Water Use", "Power Use": "Power Use"})

df0["Date"] = df0["Date"].astype(str)
df0["Water Use"] = df0["Water Use"].astype(float)
df0["Power Use"] = df0["Power Use"].astype(int)

df0 = df0[["Date", "Water Use", "Power Use"]]

df0.to_csv("autopipeline-benchmarks/github-pipelines/length1_46/target_multisource_mcts.csv", index=False)