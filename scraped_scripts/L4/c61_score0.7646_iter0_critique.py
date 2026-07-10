import pandas as pd

def clean_int_column(s):
    return pd.to_numeric(s.str.replace(r'\s', '', regex=True), errors='coerce').fillna(0).astype(int)

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

# Clean 'Población resto' as string, strip spaces
df_all['Población resto'] = df_all['Población resto'].astype(str).str.strip()

# Convert other columns to int after removing spaces
df_all['N.°'] = clean_int_column(df_all['N.°'].astype(str))
df_all['Municipio'] = clean_int_column(df_all['Municipio'].astype(str))
df_all['Departamento'] = clean_int_column(df_all['Departamento'].astype(str))
df_all['Población cabecera'] = clean_int_column(df_all['Población cabecera'].astype(str))
df_all['Población Total'] = clean_int_column(df_all['Población Total'].astype(str))

# Output with columns in the exact order of target schema
df_all = df_all[['Población resto', 'N.°', 'Municipio', 'Departamento', 'Población cabecera', 'Población Total']]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_61/target_multisource_mcts.csv", index=False)