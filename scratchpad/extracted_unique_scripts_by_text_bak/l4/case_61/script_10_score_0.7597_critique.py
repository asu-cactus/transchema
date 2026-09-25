import pandas as pd

def clean_int_column(s):
    # Remove spaces and non-breaking spaces, then convert to int
    return pd.to_numeric(s.astype(str).str.replace(r'\s+', '', regex=True).str.replace(' ', '', regex=False), errors='coerce').fillna(0).astype(int)

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_61/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

# Clean numeric columns
df_all['N.°'] = clean_int_column(df_all['N.°'])
df_all['Población cabecera'] = clean_int_column(df_all['Población cabecera'])
df_all['Población resto'] = df_all['Población resto'].astype(str)  # keep as string
df_all['Población Total'] = clean_int_column(df_all['Población Total'])

# Map 'Municipio' and 'Departamento' string columns to integer IDs consistently
# Combine unique values from all data
municipio_codes, municipio_uniques = pd.factorize(df_all['Municipio'])
departamento_codes, departamento_uniques = pd.factorize(df_all['Departamento'])

df_all['Municipio'] = municipio_codes + 1  # +1 to start IDs from 1 to match target examples
df_all['Departamento'] = departamento_codes + 1

# Group by the key columns and sum the population columns
grouped = df_all.groupby(['Población resto', 'N.°', 'Municipio', 'Departamento'], dropna=False, as_index=False).agg({
    'Población cabecera': 'sum',
    'Población Total': 'sum'
})

# Reorder columns to match target schema exactly
grouped = grouped[['Población resto', 'N.°', 'Municipio', 'Departamento', 'Población cabecera', 'Población Total']]

# Ensure correct dtypes
grouped = grouped.astype({
    'Población resto': str,
    'N.°': int,
    'Municipio': int,
    'Departamento': int,
    'Población cabecera': int,
    'Población Total': int
})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_61/target_multisource_mcts.csv", index=False)