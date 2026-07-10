import pandas as pd

path0 = "autopipeline-benchmarks/github-pipelines/length1_62/training_0.csv"

df0 = pd.read_csv(path0, index_col=0)
df1 = pd.read_csv(path0, index_col=0)

df = pd.concat([df0, df1], ignore_index=True)

df = df.rename(columns={"Text Date": "Month", "Water Use": "Water Use", "Power Use": "Power Use"})

df = df[["Month", "Water Use", "Power Use"]]

df["Water Use"] = pd.to_numeric(df["Water Use"], errors="coerce")
df["Power Use"] = pd.to_numeric(df["Power Use"], errors="coerce").fillna(0).astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_62/target_multisource_mcts.csv", index=False)