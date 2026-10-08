import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

agg_cols = ['PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']
df_grouped = df_all.groupby(['Split', 'SubjectId', 'Subject'], as_index=False)[agg_cols].sum()

df_grouped['SubjectId'] = df_grouped['SubjectId'].astype(int)
for col in agg_cols:
    df_grouped[col] = df_grouped[col].astype(int)

df_grouped = df_grouped[['Split', 'SubjectId', 'Subject', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_94/target_multisource_mcts.csv", index=False)