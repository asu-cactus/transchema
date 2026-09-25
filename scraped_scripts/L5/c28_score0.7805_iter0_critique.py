import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_28/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_28/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, how='inner', on=['CodProvincia', 'CodMunicipio'])

grouped = merged.groupby(['CP', 'CodMunicipio', 'Provincia'], as_index=False)['Poblacion'].sum()
grouped = grouped.rename(columns={'Poblacion': 'SumPoblacion', 'CodMunicipio': 'Municipio'})

result = grouped[['CP', 'Municipio', 'SumPoblacion', 'Provincia']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_28/target_multisource_mcts.csv", index=False)