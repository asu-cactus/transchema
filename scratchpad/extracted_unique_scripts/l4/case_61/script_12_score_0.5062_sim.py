import pandas as pd

def clean_int_column(s):
    if s.dtype == object:
        s = s.str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False)
    return pd.to_numeric(s, errors='coerce').astype('Int64')

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_61/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df['Población resto'] = df['Población resto'].astype(str).str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False)
df['Población resto'] = df['Población resto']

df['N.°'] = clean_int_column(df['N.°'])
df['Municipio'] = clean_int_column(df['Municipio'])
df['Departamento'] = clean_int_column(df['Departamento'])
df['Población cabecera'] = clean_int_column(df['Población cabecera'])
df['Población Total'] = clean_int_column(df['Población Total'])

df = df[['Población resto', 'N.°', 'Municipio', 'Departamento', 'Población cabecera', 'Población Total']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_61/target_multisource_mcts.csv", index=False)