import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_94/training_0.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_94/training_0.csv", index_col=0)

union_df = pd.concat([df0, df1, df2], ignore_index=True)

grouped = union_df.groupby(union_df.columns[0], as_index=False).sum()

grouped = grouped.astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_94/target_multisource_mcts.csv", index=False)