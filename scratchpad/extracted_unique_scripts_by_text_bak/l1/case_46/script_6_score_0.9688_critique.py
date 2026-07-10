import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_46/training_0.csv", index_col=0)

df0["Text Date"] = df0["Text Date"].str.strip()

agg = df0.groupby("Text Date", as_index=False).agg({"Water Use": "sum", "Power Use": "sum"})

agg["Date"] = agg["Text Date"]

agg = agg.drop(columns=["Text Date"])

agg = agg[["Date", "Water Use", "Power Use"]]

agg["Water Use"] = agg["Water Use"].astype(float)

agg["Power Use"] = agg["Power Use"].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_46/target_multisource_mcts.csv", index=False)