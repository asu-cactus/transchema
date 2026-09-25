import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_28/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_28/training_1.csv", index_col=0)

merged = pd.merge(df1, df0, on=['CodProvincia', 'CodMunicipio', 'Municipio'], how='inner')

grouped = merged.groupby(['CodProvincia', 'CodMunicipio', 'Municipio', 'Provincia'], as_index=False).agg({
    'Poblacion': 'sum',
    'CP': 'first'
})

grouped.rename(columns={
    'CodProvincia': 'CP',
    'CodMunicipio': 'Municipio',
    'Poblacion': 'SumPoblacion'
}, inplace=True)

result = grouped[['CP', 'Municipio', 'SumPoblacion', 'Provincia']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_28/target_multisource_mcts.csv", index=False)