import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_21/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_21/training_0.csv", index_col=0)

df_union = pd.concat([df0, df1], ignore_index=True)
result = df_union.groupby("Major_category", as_index=False)["Median"].mean()
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_21/target_multisource_mcts.csv", index=False)