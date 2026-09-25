import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_48/training_0.csv", index_col=0)
df0_grouped = df0.groupby("Text Date", as_index=False).agg({"Water Use": "sum", "Power Use": "sum"})
df0_grouped = df0_grouped.rename(columns={"Text Date": "Date", "Water Use": "Water Use", "Power Use": "Power Use"})
df0_grouped["Date"] = df0_grouped["Date"].astype(str)
df0_grouped["Water Use"] = df0_grouped["Water Use"].astype(float)
df0_grouped["Power Use"] = df0_grouped["Power Use"].astype(int)

df0_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_48/target_multisource_mcts.csv", index=False)