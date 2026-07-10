import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_28/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_28/training_1.csv", index_col=0)

# Join on CodProvincia and CodMunicipio only
merged = pd.merge(df1, df0, on=['CodProvincia', 'CodMunicipio'], how='inner')

# Group by CP and Municipio (from df1: CP=CodProvincia, Municipio=CodMunicipio)
grouped = merged.groupby(['CodProvincia', 'CodMunicipio'], as_index=False).agg({
    'Poblacion': 'sum',
    'Provincia': 'first'
})

# Rename columns to match target schema
grouped.rename(columns={
    'CodProvincia': 'CP',
    'CodMunicipio': 'Municipio',
    'Poblacion': 'SumPoblacion'
}, inplace=True)

# Reorder columns as per target schema
result = grouped[['CP', 'Municipio', 'SumPoblacion', 'Provincia']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_28/target_multisource_mcts.csv", index=False)