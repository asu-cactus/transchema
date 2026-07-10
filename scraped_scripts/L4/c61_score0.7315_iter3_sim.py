import pandas as pd

def clean_number_column(col):
    return col.str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False).astype(int)

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_61/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

df_all['Población cabecera'] = clean_number_column(df_all['Población cabecera'])
df_all['Población resto'] = clean_number_column(df_all['Población resto'])
df_all['Población Total'] = clean_number_column(df_all['Población Total'])

grouped = df_all.groupby(['N.°', 'Municipio', 'Departamento'], as_index=False).agg({
    'Población cabecera': 'sum',
    'Población resto': 'sum',
    'Población Total': 'sum'
})

grouped['N.°'] = grouped['N.°'].astype(int)
grouped['Municipio'] = grouped['Municipio'].astype(int, errors='ignore') if grouped['Municipio'].dtype != 'int64' else grouped['Municipio']
grouped['Departamento'] = grouped['Departamento'].astype(int, errors='ignore') if grouped['Departamento'].dtype != 'int64' else grouped['Departamento']

grouped['Población resto'] = grouped['Población resto'].astype(str)
grouped['Población cabecera'] = grouped['Población cabecera'].astype(int)
grouped['Población Total'] = grouped['Población Total'].astype(int)

grouped = grouped[['Población resto', 'N.°', 'Municipio', 'Departamento', 'Población cabecera', 'Población Total']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_61/target_multisource_mcts.csv", index=False)