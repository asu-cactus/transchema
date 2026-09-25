import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_28/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_28/training_1.csv", index_col=0)

agg_0 = df0.groupby(['CodProvincia', 'Provincia', 'CodMunicipio', 'Municipio'], as_index=False)['Poblacion'].nunique()
agg_0.rename(columns={'Poblacion': 'SumPoblacion'}, inplace=True)

merged = pd.merge(agg_0, df1, how='inner', on=['CodProvincia', 'CodMunicipio', 'Municipio'])

result = merged[['CP', 'CodMunicipio', 'SumPoblacion', 'Provincia']]
result.rename(columns={'CodMunicipio': 'Municipio'}, inplace=True)
result = result.astype({'CP': 'int64', 'Municipio': 'int64', 'SumPoblacion': 'int64', 'Provincia': 'string'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_28/target_multisource_mcts.csv", index=False)