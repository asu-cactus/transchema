import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_3/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_3/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_3/training_2.csv", index_col=0)

df_union = pd.concat([df0, df1, df2], ignore_index=True)

result = df_union.groupby("Major_category", as_index=False)["Median"].median()

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_3/target_multisource_mcts.csv", index=False)