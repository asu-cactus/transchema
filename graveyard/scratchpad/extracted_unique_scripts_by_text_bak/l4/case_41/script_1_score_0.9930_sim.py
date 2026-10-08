import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

agg_df = df_all.groupby('y').agg(
    x=('x', 'count'),
    x_avg=('x', 'mean'),
    label_count_distinct=('label', pd.Series.nunique)
).reset_index()

agg_df['x'] = agg_df['x'].astype(int)
agg_df['label'] = agg_df['label_count_distinct'].astype(int)
agg_df['x'] = agg_df['x_avg'].round().astype(int)
agg_df = agg_df[['y', 'x', 'label']]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts.csv", index=False)