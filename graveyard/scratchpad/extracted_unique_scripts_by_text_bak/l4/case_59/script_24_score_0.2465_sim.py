import pandas as pd

def clean_int_column(s):
    return pd.to_numeric(s.str.replace(r'\s', '', regex=True).str.replace(' ', '', regex=False), errors='coerce').astype('Int64')

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_59/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    for col in ['N.°', 'Municipio']:
        df[col] = clean_int_column(df[col].astype(str))
    for col in ['Población cabecera', 'Población resto', 'Población Total']:
        df[col] = clean_int_column(df[col].astype(str))
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

agg = df_all.groupby(['Departamento', 'N.°', 'Municipio'], dropna=False).agg({
    'Población cabecera': 'sum',
    'Población resto': 'sum',
    'Población Total': 'sum'
}).reset_index()

agg = agg.astype({
    'Departamento': 'string',
    'N.°': 'Int64',
    'Municipio': 'Int64',
    'Población cabecera': 'Int64',
    'Población resto': 'Int64',
    'Población Total': 'Int64'
})

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_59/target_multisource_mcts.csv", index=False)