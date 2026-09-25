import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_11/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_11/training_1.csv', index_col=0)
df2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_11/training_2.csv', index_col=0)

df_union = pd.concat([df0, df1, df2], ignore_index=True)
df_grouped = df_union.groupby('sex', as_index=False)['births'].sum()
df_grouped['sex'] = df_grouped['sex'].astype(str)
df_grouped['births'] = df_grouped['births'].astype(int)

df_grouped.to_csv('autopipeline-benchmarks/github-pipelines/length1_11/target_multisource_mcts.csv', index=False)