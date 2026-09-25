import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_95/training_0.csv", index_col=0)
df_union = pd.concat([df0], ignore_index=True)
df_grouped = df_union.groupby("customer_id", as_index=False).agg({"date": "min"})
df_grouped["customer_id"] = df_grouped["customer_id"].astype(int)
df_grouped["date"] = df_grouped["date"].astype(str)
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_95/target_multisource_mcts.csv", index=False)