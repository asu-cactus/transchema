import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_60/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

def clean_int_column(col):
    return col.astype(str).str.replace(r'\s', '', regex=True).str.replace(' ', '', regex=False).str.replace(',', '').astype(int)

df_all['N.°'] = df_all['N.°'].astype(int)
df_all['Municipio'] = df_all['Municipio'].astype(str)
df_all['Departamento'] = df_all['Departamento'].astype(str).str.strip()

df_all['Población cabecera'] = clean_int_column(df_all['Población cabecera'])
df_all['Población resto'] = clean_int_column(df_all['Población resto'])
df_all['Población Total'] = clean_int_column(df_all['Población Total'])

# Encode Departamento as categorical codes + 1 to match target integer codes
df_all['Departamento'] = df_all['Departamento'].astype('category').cat.codes + 1

# Group by Municipio, N.°, Departamento and sum population columns
df_all = df_all.groupby(['Municipio', 'N.°', 'Departamento'], as_index=False).agg({
    'Población cabecera': 'sum',
    'Población resto': 'sum',
    'Población Total': 'sum'
})

df_all = df_all[['Municipio', 'N.°', 'Departamento', 'Población cabecera', 'Población resto', 'Población Total']]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_60/target_multisource_mcts.csv", index=False)