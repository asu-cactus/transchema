import pandas as pd

def clean_int_column(s):
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

df_all['N.°'] = clean_int_column(df_all['N.°'])
df_all['Municipio'] = clean_int_column(df_all['Municipio'])
df_all['Departamento'] = clean_int_column(df_all['Departamento'])
df_all['Población cabecera'] = clean_int_column(df_all['Población cabecera'])
df_all['Población Total'] = clean_int_column(df_all['Población Total'])

grouped = df_all.groupby('Población resto', dropna=False, as_index=False).agg({
    'N.°': 'sum',
    'Municipio': 'sum',
    'Departamento': 'sum',
    'Población cabecera': 'sum',
    'Población Total': 'sum'
})

grouped = grouped.astype({
    'Población resto': str,
    'N.°': int,
    'Municipio': int,
    'Departamento': int,
    'Población cabecera': int,
    'Población Total': int
})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_61/target_multisource_mcts.csv", index=False)