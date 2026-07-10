import pandas as pd

df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_10/training_0.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_10/training_1.csv", index_col=0)

agg_df2 = df2.groupby("city", as_index=False)["driver_count"].sum()
agg_df2["driver_count"] = agg_df2["driver_count"].astype(int)

agg_df2.to_csv("autopipeline-benchmarks/github-pipelines/length2_10/target_multisource_mcts.csv", index=False)