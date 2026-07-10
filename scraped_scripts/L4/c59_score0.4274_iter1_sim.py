import pandas as pd

def clean_int_column(s):
    if s.dtype == object:
        s = s.str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False)
    return pd.to_numeric(s, errors='coerce').fillna(0).astype(int)

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_59/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

df_all['Departamento'] = df_all['Departamento'].astype(str)
df_all['N.°'] = clean_int_column(df_all['N.°'])
df_all['Municipio'] = clean_int_column(df_all['Municipio'])
df_all['Población cabecera'] = clean_int_column(df_all['Población cabecera'])
df_all['Población resto'] = clean_int_column(df_all['Población resto'])
df_all['Población Total'] = clean_int_column(df_all['Población Total'])

df_all = df_all[['Departamento', 'N.°', 'Municipio', 'Población cabecera', 'Población resto', 'Población Total']]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_59/target_multisource_mcts.csv", index=False)