import pandas as pd

def clean_int_column(s):
    return pd.to_numeric(s.str.replace(r'\s', '', regex=True), errors='coerce').fillna(0).astype(int)

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_59/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    df['N.°'] = clean_int_column(df['N.°'].astype(str))
    df['Municipio'] = clean_int_column(df['Municipio'].astype(str))
    df['Población cabecera'] = clean_int_column(df['Población cabecera'].astype(str))
    df['Población resto'] = clean_int_column(df['Población resto'].astype(str))
    df['Población Total'] = clean_int_column(df['Población Total'].astype(str))
    dfs.append(df)

union_df = pd.concat(dfs, ignore_index=True)

agg_df = union_df.groupby('Departamento', as_index=False).agg({
    'N.°': 'sum',
    'Municipio': 'count',
    'Población cabecera': 'sum',
    'Población resto': 'sum',
    'Población Total': 'sum'
})

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_59/target_multisource_mcts.csv", index=False)