import pandas as pd

def clean_int_column(s):
    # Remove spaces and non-breaking spaces, convert to numeric Int64
    return pd.to_numeric(s.str.replace(r'\s', '', regex=True).str.replace(' ', '', regex=False), errors='coerce').astype('Int64')

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_59/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

for df in dfs:
    df['Departamento'] = df['Departamento'].astype(str)
    df['N.°'] = clean_int_column(df['N.°'].astype(str))
    df['Municipio'] = clean_int_column(df['Municipio'].astype(str))
    df['Población cabecera'] = clean_int_column(df['Población cabecera'].astype(str))
    df['Población resto'] = clean_int_column(df['Población resto'].astype(str))
    df['Población Total'] = clean_int_column(df['Población Total'].astype(str))

df_all = pd.concat(dfs, ignore_index=True)

# Group by Departamento, N.°, Municipio and sum the population columns
df_grouped = df_all.groupby(['Departamento', 'N.°', 'Municipio'], dropna=False, as_index=False).agg({
    'Población cabecera': 'sum',
    'Población resto': 'sum',
    'Población Total': 'sum'
})

# Reorder columns to match target schema exactly
df_grouped = df_grouped[['Departamento', 'N.°', 'Municipio', 'Población cabecera', 'Población resto', 'Población Total']]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_59/target_multisource_mcts.csv", index=False)