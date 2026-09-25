import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_46/training_0.csv", index_col=0)
df = df.rename(columns={"Text Date": "Date"})
df = df[["Date", "Water Use", "Power Use"]]
df["Water Use"] = df["Water Use"].astype(float)
df["Power Use"] = df["Power Use"].astype(int)
df.to_csv("autopipeline-benchmarks/github-pipelines/length1_46/target_multisource_mcts.csv", index=False)