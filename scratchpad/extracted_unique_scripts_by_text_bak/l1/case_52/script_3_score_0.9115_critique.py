import pandas as pd

df = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_52/training_0.csv', index_col=0)

df_grouped = df.groupby('condition', as_index=False).size()
df_grouped.rename(columns={'size': '0'}, inplace=True)

df_grouped.to_csv('autopipeline-benchmarks/github-pipelines/length1_52/target_multisource_mcts.csv', index=False)