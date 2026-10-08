import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_28/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_28/training_1.csv", index_col=0)

df0_renamed = df0.rename(columns={
    'CodProvincia': 'CP',
    'CodMunicipio': 'Municipio',
    'Poblacion': 'SumPoblacion'
})[['CP', 'Municipio', 'SumPoblacion', 'Provincia']]

df1['SumPoblacion'] = 0
df1 = df1[['CP', 'Municipio', 'SumPoblacion']]
df1['Provincia'] = pd.NA

df_union = pd.concat([df0_renamed, df1], ignore_index=True, sort=False)

df_union['CP'] = df_union['CP'].astype('Int64')
df_union['Municipio'] = df_union['Municipio'].astype('Int64')
df_union['SumPoblacion'] = df_union['SumPoblacion'].astype('Int64')
df_union['Provincia'] = df_union['Provincia'].astype('string')

df_union.to_csv("autopipeline-benchmarks/github-pipelines/length5_28/target_multisource_mcts.csv", index=False)