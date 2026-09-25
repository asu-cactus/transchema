import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_3.csv", index_col=0)

df0 = df0.rename(columns={'y': 'y_0', 'label': 'label_0'})
df1 = df1.rename(columns={'y': 'y_1', 'label': 'label_1'})
df2 = df2.rename(columns={'y': 'y_2', 'label': 'label_2'})
df3 = df3.rename(columns={'y': 'y_3', 'label': 'label_3'})

df_merged = df0.merge(df1, on='x', how='inner', suffixes=('', '_1'))
df_merged = df_merged.merge(df2, on='x', how='inner', suffixes=('', '_2'))
df_merged = df_merged.merge(df3, on='x', how='inner', suffixes=('', '_3'))

unpivot_data = []
for i, suffix in enumerate(['_0', '_1', '_2', '_3']):
    y_col = f'y{suffix}'
    label_col = f'label{suffix}'
    temp_df = df_merged[['x', y_col, label_col]].copy()
    temp_df.columns = ['x', 'y', 'label']
    unpivot_data.append(temp_df)

df_unpivot = pd.concat(unpivot_data, ignore_index=True)

label_map = {v: k for k, v in enumerate(sorted(df_unpivot['label'].unique()))}
df_unpivot['label'] = df_unpivot['label'].map(label_map)

df_unpivot['y'] = df_unpivot['y'].astype(float)
df_unpivot['x'] = df_unpivot['x'].astype(int)
df_unpivot['label'] = df_unpivot['label'].astype(int)

df_unpivot.to_csv("autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts.csv", index=False)