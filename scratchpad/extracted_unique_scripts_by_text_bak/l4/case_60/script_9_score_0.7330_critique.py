import pandas as pd
import numpy as np

def clean_number_column(col):
    # Remove spaces, non-breaking spaces, commas, dots, then convert to numeric
    return pd.to_numeric(
        col.astype(str)
           .str.replace(r'\s', '', regex=True)
           .str.replace(' ', '', regex=False)  # non-breaking space
           .str.replace(',', '', regex=False)
           .str.replace('.', '', regex=False)
           .replace('', np.nan),
        errors='coerce'
    )

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_60/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    for col in ['Población cabecera', 'Población resto', 'Población Total']:
        df[col] = clean_number_column(df[col])
    df['N.°'] = pd.to_numeric(df['N.°'], errors='coerce')
    dfs.append(df)

# UNION all source tables
df_all = pd.concat(dfs, ignore_index=True)

# Convert Departamento string to integer codes (consistent)
# Factorize Departamento to get integer codes starting from 1 (to match target examples)
df_all['Departamento'] = pd.factorize(df_all['Departamento'])[0] + 1

# Convert columns to correct types
df_all['Municipio'] = df_all['Municipio'].astype(str)
df_all['N.°'] = df_all['N.°'].round().astype('Int64')
df_all['Departamento'] = df_all['Departamento'].astype('Int64')
df_all['Población cabecera'] = df_all['Población cabecera'].round().astype('Int64')
df_all['Población resto'] = df_all['Población resto'].round().astype('Int64')
df_all['Población Total'] = df_all['Población Total'].round().astype('Int64')

# Select columns in target schema order
result = df_all[['Municipio', 'N.°', 'Departamento', 'Población cabecera', 'Población resto', 'Población Total']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_60/target_multisource_mcts.csv", index=False)