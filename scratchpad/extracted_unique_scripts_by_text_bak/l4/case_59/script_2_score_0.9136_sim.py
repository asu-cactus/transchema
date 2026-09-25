import pandas as pd

def clean_int_column(s):
    return pd.to_numeric(s.astype(str).str.replace(r'\s+', '', regex=True).str.replace(' ', '', regex=False), errors='coerce').fillna(0).astype(int)

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_59/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    for col in ['N.°', 'Municipio', 'Población cabecera', 'Población resto', 'Población Total']:
        df[col] = clean_int_column(df[col])
    dfs.append(df)

union_df = pd.concat(dfs, ignore_index=True)

grouped = union_df.groupby('Departamento', as_index=False).agg({
    'N.°': 'count',
    'Municipio': 'sum',
    'Población cabecera': 'min',
    'Población resto': 'min',
    'Población Total': 'min'
})

grouped = grouped.rename(columns={'N.°': 'N.°'})

grouped = grouped[['Departamento', 'N.°', 'Municipio', 'Población cabecera', 'Población resto', 'Población Total']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_59/target_multisource_mcts.csv", index=False)