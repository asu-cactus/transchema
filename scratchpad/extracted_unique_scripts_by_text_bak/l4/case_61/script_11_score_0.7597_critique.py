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

# Concatenate all source tables first
df_all = pd.concat(dfs, ignore_index=True)

# Encode 'Departamento' and 'Municipio' consistently after concatenation
df_all['Departamento'] = df_all['Departamento'].astype('category').cat.codes + 1
df_all['Municipio'] = df_all['Municipio'].astype('category').cat.codes + 1

# Clean and convert population columns except 'Población resto' which remains string
for col in ['Población cabecera', 'Población Total']:
    df_all[col] = df_all[col].astype(str).str.replace('\xa0', '').str.replace(' ', '').str.replace('.', '').str.replace(',', '').astype(int)

# 'Población resto' remains string but clean spaces/non-breaking spaces (keep as string)
df_all['Población resto'] = df_all['Población resto'].astype(str).str.replace('\xa0', ' ').str.strip()

# Convert 'N.°' to int
df_all['N.°'] = df_all['N.°'].astype(int)

# Reorder columns to match target schema exactly
df_all = df_all[['Población resto', 'N.°', 'Municipio', 'Departamento', 'Población cabecera', 'Población Total']]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_61/target_multisource_mcts.csv", index=False)