import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_40/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_all['y'] = pd.to_numeric(df_all['y'], errors='coerce')

agg_df = df_all.groupby('x').agg(
    y_count=('y', 'count'),
    y_avg=('y', 'mean'),
    y_max=('y', 'max')
).reset_index()

agg_df['y'] = 1
agg_df['label'] = 1

agg_df = agg_df[['x', 'y', 'label']]

agg_df['x'] = agg_df['x'].astype(float)
agg_df['y'] = agg_df['y'].astype(int)
agg_df['label'] = agg_df['label'].astype(int)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_40/target_multisource_mcts.csv", index=False)