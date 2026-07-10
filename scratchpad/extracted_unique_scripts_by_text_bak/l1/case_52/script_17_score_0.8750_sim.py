import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_52/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_52/training_0.csv', index_col=0)

df_union = pd.concat([df0, df1], ignore_index=True)
df_grouped = df_union.groupby('condition', as_index=False)['click'].sum()
df_grouped.rename(columns={'click': '0'}, inplace=True)

df_grouped.to_csv('autopipeline-benchmarks/github-pipelines/length1_52/target_multisource_mcts.csv', index=False)