import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_100/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_100/training_1.csv", index_col=0)

df_union = pd.concat([df0, df1], ignore_index=True, sort=False)

df_unpivot = df_union.melt(id_vars=['Rank'], value_name='0')
df_unpivot = df_unpivot[['Rank', '0']]
df_unpivot['Rank'] = pd.to_numeric(df_unpivot['Rank'], errors='coerce').astype('Int64')
df_unpivot['0'] = pd.to_numeric(df_unpivot['0'], errors='coerce').fillna(0).astype(int)

df_unpivot.to_csv("autopipeline-benchmarks/github-pipelines/length3_100/target_multisource_mcts.csv", index=False)