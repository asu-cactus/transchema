import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_60/training_0.csv", index_col=0)

agg_df0 = df0.groupby("type", as_index=False)["driver_count"].sum()
agg_df0["driver_count"] = agg_df0["driver_count"].astype(int)

max_driver_count = agg_df0["driver_count"].max()
filtered_df = agg_df0[agg_df0["driver_count"] == max_driver_count]

filtered_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_60/target_multisource_mcts.csv", index=False)