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

# Clean population columns: remove spaces and non-breaking spaces, convert to int
for col in ['Población resto', 'Población cabecera', 'Población Total']:
    df_all[col] = df_all[col].astype(str).str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False)
    df_all[col] = pd.to_numeric(df_all[col], errors='coerce').fillna(0).astype(int)

# Convert 'N.°' to int
df_all['N.°'] = pd.to_numeric(df_all['N.°'], errors='coerce').fillna(0).astype(int)

# Convert 'Municipio' and 'Departamento' to categorical codes starting at 1
df_all['Municipio'] = df_all['Municipio'].astype(str).str.strip()
df_all['Municipio'] = df_all['Municipio'].astype('category').cat.codes + 1

df_all['Departamento'] = df_all['Departamento'].astype(str).str.strip()
df_all['Departamento'] = df_all['Departamento'].astype('category').cat.codes + 1

# Group by key columns and sum population columns
df_grouped = df_all.groupby(['N.°', 'Municipio', 'Departamento'], as_index=False).agg({
    'Población resto': 'sum',
    'Población cabecera': 'sum',
    'Población Total': 'sum'
})

# Convert 'Población resto' back to string as per target schema
df_grouped['Población resto'] = df_grouped['Población resto'].astype(str)

# Reorder columns to match target schema
df_grouped = df_grouped[['Población resto', 'N.°', 'Municipio', 'Departamento', 'Población cabecera', 'Población Total']]

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_61/target_multisource_mcts.csv", index=False)