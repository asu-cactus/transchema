import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_95/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_95/training_0.csv", index_col=0)

union_df = pd.concat([df0, df1], ignore_index=True)
grouped = union_df.groupby("customer_id", as_index=False).agg({"date": "min"})
grouped["customer_id"] = grouped["customer_id"].astype(int)
grouped["date"] = grouped["date"].astype(str)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_95/target_multisource_mcts.csv", index=False)