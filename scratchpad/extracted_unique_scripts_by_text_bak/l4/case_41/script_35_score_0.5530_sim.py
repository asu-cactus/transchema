import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_all['label'] = df_all['label'].astype('category').cat.codes
df_all['x'] = df_all['x'].round().astype(int)

agg_df = df_all.groupby(['x', 'label'], as_index=False)['y'].sum()

agg_df['label'] = agg_df['label'].astype(int)
agg_df['x'] = agg_df['x'].astype(int)
agg_df['y'] = agg_df['y'].astype(float)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts.csv", index=False)