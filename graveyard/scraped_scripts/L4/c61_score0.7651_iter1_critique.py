import pandas as pd

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

# Clean numeric columns by removing spaces, non-breaking spaces, commas, then convert to int
def clean_int_column(col):
    return col.astype(str).str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False).str.replace(',', '', regex=False).astype(int)

df_all['Población resto'] = clean_int_column(df_all['Población resto'])
df_all['Población cabecera'] = clean_int_column(df_all['Población cabecera'])
df_all['Población Total'] = clean_int_column(df_all['Población Total'])
df_all['N.°'] = df_all['N.°'].astype(int)

# Factorize Municipio and Departamento to integers starting from 1
df_all['Municipio'] = pd.factorize(df_all['Municipio'])[0] + 1
df_all['Departamento'] = pd.factorize(df_all['Departamento'])[0] + 1

# Group by 'N.°' (primary key) and take first of other columns
df_grouped = df_all.groupby('N.°', as_index=False).agg({
    'Población resto': 'first',
    'Municipio': 'first',
    'Departamento': 'first',
    'Población cabecera': 'first',
    'Población Total': 'first'
})

# Convert 'Población resto' back to string with non-breaking spaces as thousands separator
def int_to_nbsp_str(x):
    # Format integer with normal spaces as thousands separator, then replace spaces with non-breaking spaces
    return f"{x:,}".replace(',', ' ').replace(' ', '\xa0')

df_grouped['Población resto'] = df_grouped['Población resto'].apply(int_to_nbsp_str)

# Reorder columns to match target schema
df_grouped = df_grouped[['Población resto', 'N.°', 'Municipio', 'Departamento', 'Población cabecera', 'Población Total']]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_61/target_multisource_mcts.csv", index=False)