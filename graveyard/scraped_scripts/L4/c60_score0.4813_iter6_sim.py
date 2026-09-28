import pandas as pd

def clean_int_column(s):
    return pd.to_numeric(s.str.replace(r'\s', '', regex=True), errors='coerce').astype('Int64')

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_60/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    df['N.°'] = clean_int_column(df['N.°'].astype(str))
    df['Municipio'] = df['Municipio'].astype(str)
    df['Departamento'] = df['Departamento'].astype(str)
    df['Población cabecera'] = clean_int_column(df['Población cabecera'].astype(str))
    df['Población resto'] = clean_int_column(df['Población resto'].astype(str))
    df['Población Total'] = clean_int_column(df['Población Total'].astype(str))
    dfs.append(df)

result = pd.concat(dfs, ignore_index=True)

result['Departamento'] = pd.to_numeric(result['Departamento'], errors='coerce').astype('Int64')

result = result[['Municipio', 'N.°', 'Departamento', 'Población cabecera', 'Población resto', 'Población Total']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_60/target_multisource_mcts.csv", index=False)