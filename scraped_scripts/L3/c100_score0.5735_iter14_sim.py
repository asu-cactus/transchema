import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_100/training_0.csv", index_col=0)

unpivot_cols = ['Documents', 'Citable documents', 'Citations', 'Self-citations', 'Citations per document', 'H index']
df_unpivot = df0.melt(id_vars=['Rank'], value_vars=unpivot_cols, var_name='variable', value_name='value')

df_grouped = df_unpivot.groupby('Rank', as_index=False)['value'].sum()
df_grouped['Rank'] = df_grouped['Rank'].astype(int)
df_grouped['0'] = df_grouped['value'].astype(int)
result = df_grouped[['Rank', '0']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_100/target_multisource_mcts.csv", index=False)