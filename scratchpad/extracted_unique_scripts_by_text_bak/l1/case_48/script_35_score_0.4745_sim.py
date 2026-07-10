import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_48/training_0.csv", index_col=0)

df = df0.rename(columns={"Text Date": "Date", "Water Use": "Water Use", "Power Use": "Power Use"})
df = df[["Date", "Water Use", "Power Use"]]

df["Water Use"] = df["Water Use"].astype(float)
df["Power Use"] = df["Power Use"].astype(int)
df["Date"] = df["Date"].astype(str)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_48/target_multisource_mcts.csv", index=False)