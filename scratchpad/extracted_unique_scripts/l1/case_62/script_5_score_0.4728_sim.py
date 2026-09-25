import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_62/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_62/training_0.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True)

df = df.rename(columns={"Text Date": "Month", "Water Use": "Water Use", "Power Use": "Power Use"})

df = df[["Month", "Water Use", "Power Use"]]

df["Month"] = df["Month"].astype(str)
df["Water Use"] = pd.to_numeric(df["Water Use"], errors='coerce').astype(float)
df["Power Use"] = pd.to_numeric(df["Power Use"], errors='coerce').astype('Int64')

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_62/target_multisource_mcts.csv", index=False)