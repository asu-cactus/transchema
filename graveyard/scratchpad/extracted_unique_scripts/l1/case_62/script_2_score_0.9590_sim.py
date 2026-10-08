import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_62/training_0.csv", index_col=0)

agg_df = df0.groupby("Value Date", as_index=False).agg({"Water Use": "sum", "Power Use": "sum"})

agg_df["Month"] = agg_df["Value Date"]
agg_df = agg_df.drop(columns=["Value Date"])

agg_df["Water Use"] = agg_df["Water Use"].astype(float)
agg_df["Power Use"] = agg_df["Power Use"].astype(int)

agg_df = agg_df[["Month", "Water Use", "Power Use"]]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_62/target_multisource_mcts.csv", index=False)