import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_3.csv", index_col=0)

df01 = pd.merge(df0, df1, on=['x', 'y'], suffixes=('_0', '_1'))

df01_grouped = df01.groupby('y', as_index=False).first()

df2_renamed = df2.rename(columns={'label': 'label_2'})
df3_renamed = df3.rename(columns={'label': 'label_3'})

df_all = df01_grouped.merge(df2_renamed, on=['x', 'y'], how='outer')
df_all = df_all.merge(df3_renamed, on=['x', 'y'], how='outer')

def label_to_int(label):
    if pd.isna(label):
        return 0
    if isinstance(label, str):
        return 1
    return int(label)

df_all['label_0'] = df_all['label_0'].apply(label_to_int) if 'label_0' in df_all else 0
df_all['label_1'] = df_all['label_1'].apply(label_to_int) if 'label_1' in df_all else 0
df_all['label_2'] = df_all['label_2'].apply(label_to_int) if 'label_2' in df_all else 0
df_all['label_3'] = df_all['label_3'].apply(label_to_int) if 'label_3' in df_all else 0

df_all['label'] = df_all[['label_0', 'label_1', 'label_2', 'label_3']].max(axis=1)

df_result = df_all[['y', 'x', 'label']]

df_result['x'] = df_result['x'].astype(int)
df_result['y'] = df_result['y'].astype(float)
df_result['label'] = df_result['label'].astype(int)

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts.csv", index=False)