import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_48/training_0.csv", index_col=0)

agg = df0.groupby("Value Date").agg({"Water Use": "mean", "Power Use": "mean"}).reset_index()

agg["Date"] = agg["Value Date"].astype(str)
agg["Water Use"] = agg["Water Use"].astype(float)
agg["Power Use"] = agg["Power Use"].round().astype(int)

result = agg[["Date", "Water Use", "Power Use"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_48/target_multisource_mcts.csv", index=False)