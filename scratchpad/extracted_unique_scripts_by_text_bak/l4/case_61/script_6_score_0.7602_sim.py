import pandas as pd

def clean_number_column(s):
    return pd.to_numeric(s.str.replace(r'\s', '', regex=True).str.replace(' ', '', regex=False), errors='coerce')

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

df_all['Población cabecera'] = clean_number_column(df_all['Población cabecera'])
df_all['Población resto'] = clean_number_column(df_all['Población resto'])
df_all['Población Total'] = clean_number_column(df_all['Población Total'])

grouped = df_all.groupby(['N.°', 'Municipio', 'Departamento'], dropna=False).agg({
    'Población cabecera': 'mean',
    'Población resto': 'mean',
    'Población Total': 'mean'
}).reset_index()

grouped['N.°'] = grouped['N.°'].astype('Int64')
grouped['Municipio'] = grouped['Municipio'].astype('Int64', errors='ignore')
grouped['Departamento'] = grouped['Departamento'].astype('Int64', errors='ignore')

grouped['Población cabecera'] = grouped['Población cabecera'].round().astype('Int64')
grouped['Población resto'] = grouped['Población resto'].round().astype('Int64')
grouped['Población Total'] = grouped['Población Total'].round().astype('Int64')

grouped['Población resto'] = grouped['Población resto'].astype(str).str.replace(r'(\d)(?=(\d{3})+$)', r'\1 ', regex=True).str.strip()

grouped = grouped[['Población resto', 'N.°', 'Municipio', 'Departamento', 'Población cabecera', 'Población Total']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_61/target_multisource_mcts.csv", index=False)