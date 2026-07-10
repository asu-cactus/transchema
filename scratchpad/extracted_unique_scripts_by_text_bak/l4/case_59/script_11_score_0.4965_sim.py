import pandas as pd

def clean_int_column(s):
    return pd.to_numeric(s.str.replace(r'\s', '', regex=True).str.replace(r'\.', '', regex=True), errors='coerce').fillna(0).astype(int)

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_59/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    df['Población cabecera'] = clean_int_column(df['Población cabecera'])
    df['Población resto'] = clean_int_column(df['Población resto'])
    df['Población Total'] = clean_int_column(df['Población Total'])
    df['N.°'] = pd.to_numeric(df['N.°'], errors='coerce').fillna(0).astype(int)
    df['Municipio'] = pd.to_numeric(df['Municipio'], errors='coerce').fillna(0).astype(int)
    dfs.append(df)

union_df = pd.concat(dfs, ignore_index=True)

grouped = union_df.groupby(['Departamento', 'N.°', 'Municipio'], as_index=False).agg({
    'Población cabecera': 'sum',
    'Población resto': 'sum',
    'Población Total': 'sum'
})

grouped['N.°'] = grouped['N.°'].astype(int)
grouped['Municipio'] = grouped['Municipio'].astype(int)
grouped['Población cabecera'] = grouped['Población cabecera'].astype(int)
grouped['Población resto'] = grouped['Población resto'].astype(int)
grouped['Población Total'] = grouped['Población Total'].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_59/target_multisource_mcts.csv", index=False)