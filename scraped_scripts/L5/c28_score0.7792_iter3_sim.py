import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_28/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_28/training_1.csv", index_col=0)

agg_0 = df0.groupby(['CodProvincia', 'CodMunicipio', 'Municipio', 'Provincia'], as_index=False)['Poblacion'].sum()
agg_0.rename(columns={'Poblacion': 'SumPoblacion'}, inplace=True)

merged = pd.merge(agg_0, df1, how='inner', on=['CodProvincia', 'CodMunicipio', 'Municipio'])

result = merged[['CP', 'CodMunicipio', 'SumPoblacion', 'Provincia']]
result.rename(columns={'CodMunicipio': 'Municipio'}, inplace=True)

result['CP'] = result['CP'].astype(int)
result['Municipio'] = result['Municipio'].astype(int)
result['SumPoblacion'] = result['SumPoblacion'].astype(int)
result['Provincia'] = result['Provincia'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_28/target_multisource_mcts.csv", index=False)