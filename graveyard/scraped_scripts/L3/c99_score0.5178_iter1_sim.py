import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_99/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_99/training_1.csv", index_col=0)

df0_sel = df0[['MOTATE_V', 'count']]
df1_sel = df1[['NOMBRE DE TIPOLOGIA', 'TOTAL DE CONSULTORIOS']].rename(columns={'NOMBRE DE TIPOLOGIA': 'MOTATE_V', 'TOTAL DE CONSULTORIOS': 'count'})

df_union = pd.concat([df0_sel, df1_sel], ignore_index=True)

df_grouped = df_union.groupby('MOTATE_V', dropna=False, as_index=False).agg({'count': 'sum'})

df_grouped['MOTATE_V'] = df_grouped['MOTATE_V'].astype(str)
df_grouped['count'] = df_grouped['count'].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_99/target_multisource_mcts.csv", index=False)