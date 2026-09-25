import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_77/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_77/training_0.csv", index_col=0)

union_df = pd.concat([df0, df1], ignore_index=True)
grouped = union_df.groupby("fac_type", as_index=False)["capacity"].sum()
grouped["capacity"] = grouped["capacity"].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_77/target_multisource_mcts.csv", index=False)