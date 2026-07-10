import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_100/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_100/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_100/training_2.csv", index_col=0)

df0_simple = df0[['Rank', 'Documents']].copy()
df0_simple['Documents'] = pd.to_numeric(df0_simple['Documents'], errors='coerce')

df_pivot = df0_simple.pivot_table(index='Rank', values='Documents', aggfunc='first').reset_index()

df_unpivot = df_pivot.melt(id_vars=['Rank'], var_name='variable', value_name='0')

df_unpivot['Rank'] = df_unpivot['Rank'].astype('Int64')
df_unpivot['0'] = pd.to_numeric(df_unpivot['0'], errors='coerce').astype('Int64')

df_unpivot = df_unpivot[['Rank', '0']]

df_unpivot.to_csv("autopipeline-benchmarks/github-pipelines/length3_100/target_multisource_mcts.csv", index=False)