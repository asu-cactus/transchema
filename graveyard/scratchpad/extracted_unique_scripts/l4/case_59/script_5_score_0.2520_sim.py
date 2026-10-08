import pandas as pd

def clean_int_column(s):
    if s.dtype == object:
        s = s.str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False)
    return pd.to_numeric(s, errors='coerce').astype('Int64')

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_59/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df['Departamento'] = df['Departamento'].astype(str)
df['N.°'] = clean_int_column(df['N.°'])
df['Municipio'] = clean_int_column(df['Municipio'])
df['Población cabecera'] = clean_int_column(df['Población cabecera'])
df['Población resto'] = clean_int_column(df['Población resto'])
df['Población Total'] = clean_int_column(df['Población Total'])

df = df[['Departamento', 'N.°', 'Municipio', 'Población cabecera', 'Población resto', 'Población Total']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_59/target_multisource_mcts.csv", index=False)