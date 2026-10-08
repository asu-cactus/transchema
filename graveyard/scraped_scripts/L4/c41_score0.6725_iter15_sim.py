import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_3.csv", index_col=0)

join_df = pd.merge(df0, df1, left_on='label', right_on='label', suffixes=('_0', '_1'))
join_df = join_df[['y_0', 'x_0', 'label']]  # keep y and x from df0, label as is

union_df = pd.concat([df2, df3], ignore_index=True)

full_df = pd.concat([join_df, union_df], ignore_index=True)

label_map = {v: i for i, v in enumerate(sorted(full_df['label'].unique()))}
full_df['label'] = full_df['label'].map(label_map)

full_df['y'] = full_df['y_0'].combine_first(full_df['y'])
full_df['x'] = full_df['x_0'].combine_first(full_df['x'])

full_df = full_df[['y', 'x', 'label']]

full_df['y'] = full_df['y'].astype(float)
full_df['x'] = full_df['x'].astype(int)
full_df['label'] = full_df['label'].astype(int)

full_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts.csv", index=False)