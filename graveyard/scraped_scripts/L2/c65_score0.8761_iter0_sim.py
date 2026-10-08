import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_65/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_65/training_1.csv", index_col=0)

df0_sub = df0[['fname']]
df1_sub = df1[['fname']]

df_all = pd.concat([df0_sub, df1_sub], ignore_index=True)

result = df_all.groupby('fname', as_index=False).size().rename(columns={'size': 'row_count'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_65/target_multisource_mcts.csv", index=False)