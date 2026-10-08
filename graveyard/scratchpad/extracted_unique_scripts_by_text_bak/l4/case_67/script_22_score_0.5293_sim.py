import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_67/training_0.csv", index_col=0)

df_melt = df0.melt(id_vars=['overs', 'Batsman on strike'], value_vars=['runs scored', 'extras'], var_name='variable', value_name='value')

df_pivot = df_melt.pivot_table(index=['Batsman on strike', 'overs'], columns='variable', values='value', aggfunc='sum').reset_index()

df_pivot.columns.name = None

df_pivot['overs'] = df_pivot['overs'].astype(float)
df_pivot['runs scored'] = df_pivot['runs scored'].astype(int)
df_pivot['extras'] = df_pivot['extras'].astype(int)

df_pivot = df_pivot.rename(columns={'Batsman on strike': 'Batsman on strike'})

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length4_67/target_multisource_mcts.csv", index=False)