import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_41/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

df['label'] = df['label'].astype('category').cat.codes

df_grouped = df.groupby(['y', 'x', 'label'], as_index=False).size()

df_grouped = df_grouped.rename(columns={'size': 'count'})

df_result = df_grouped[['y', 'x', 'label']]

df_result['y'] = df_result['y'].astype(float)
df_result['x'] = df_result['x'].astype(int)
df_result['label'] = df_result['label'].astype(int)

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length4_41/target_multisource_mcts.csv", index=False)