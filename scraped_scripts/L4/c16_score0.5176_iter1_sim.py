import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_16/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_16/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_16/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_16/training_3.csv", index_col=0)

pivot_df1 = df1.pivot_table(index=['COD_PERSONA', 'COD_INTERV', 'XTI_ESTADO', 'COD_IDCONTRA'], columns='QNU_ORDTIT', aggfunc='first').reset_index()
# After pivot, flatten columns if any multiindex
if isinstance(pivot_df1.columns, pd.MultiIndex):
    pivot_df1.columns = ['_'.join(map(str, col)).strip('_') for col in pivot_df1.columns.values]

join_1 = pd.merge(pivot_df1, df2, on='COD_PERSONA', how='inner')
join_2 = pd.merge(join_1, df3, left_on='COD_OFICIPAL', right_on='COD_OFICI', how='inner')
final_join = pd.merge(join_2, df0, on='COD_IDCONTRA', how='inner')

result = final_join[['COD_INTERV', 'XTI_ESTADO', 'COD_OFICIPAL', 'COD_SEGLOBAL', 'COD_OFICI', 'COD_NIVELOFIC']].copy()
result.rename(columns={'XTI_ESTADO': 'estado_cli'}, inplace=True)
result['COD_OFICIPAL'] = result['COD_OFICIPAL'].astype('Int64')
result['COD_SEGLOBAL'] = result['COD_SEGLOBAL'].astype('Int64')
result['COD_OFICI'] = result['COD_OFICI'].astype('Int64')
result['COD_NIVELOFIC'] = result['COD_NIVELOFIC'].astype('Int64')
result['COD_INTERV'] = result['COD_INTERV'].astype(str)
result['estado_cli'] = result['estado_cli'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_16/target_multisource_mcts.csv", index=False)