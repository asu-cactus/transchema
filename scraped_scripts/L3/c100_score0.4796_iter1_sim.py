import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_100/training_0.csv", index_col=0)
df_unpivot = df0.melt(id_vars=['Rank'], value_vars=['Documents', 'Citable documents', 'Citations', 'Self-citations', 'Citations per document', 'H index'], var_name='variable', value_name='0')
df_unpivot['Rank'] = df_unpivot['Rank'].astype(int)
df_unpivot['0'] = pd.to_numeric(df_unpivot['0'], errors='coerce').fillna(0).astype(int)
df_unpivot = df_unpivot[['Rank', '0']]
df_unpivot.to_csv("autopipeline-benchmarks/github-pipelines/length3_100/target_multisource_mcts.csv", index=False)