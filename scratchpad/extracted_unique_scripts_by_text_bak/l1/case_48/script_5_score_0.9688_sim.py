import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_48/training_0.csv", index_col=0)

df0 = df0.rename(columns={"Text Date": "Date"})

df0["Date"] = df0["Date"].astype(str)

df0["Water Use"] = df0["Water Use"].astype(float)
df0["Power Use"] = df0["Power Use"].astype(int)

result = df0.groupby("Date", as_index=False).agg({"Water Use": "sum", "Power Use": "sum"})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_48/target_multisource_mcts.csv", index=False)