import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_82/training_0.csv', index_col=0)
df_filtered = df0[df0['conservation_status'].notna()]
df_filtered = df_filtered.copy()
df_filtered['scientific_name'], _ = pd.factorize(df_filtered['scientific_name'])
result = df_filtered[['conservation_status', 'scientific_name']]
result.to_csv('autopipeline-benchmarks/github-pipelines/length1_82/target_multisource_mcts.csv', index=False)