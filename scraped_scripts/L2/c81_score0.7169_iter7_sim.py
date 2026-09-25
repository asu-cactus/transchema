import pandas as pd

df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_81/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_81/training_1.csv", index_col=0)

union_df = pd.concat([df1, df2], ignore_index=True)
grouped = union_df.groupby("city", as_index=False)["driver_count"].sum()
grouped["driver_count"] = grouped["driver_count"].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_81/target_multisource_mcts.csv", index=False)