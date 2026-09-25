import pandas as pd

def clean_int_column(s):
    if s.dtype == object:
        s = s.str.replace(r'\s', '', regex=True).str.replace(' ', '', regex=False)
        s = s.str.replace('.', '', regex=False)
        s = s.str.replace(',', '', regex=False)
        s = s.str.replace('-', '', regex=False)
    return pd.to_numeric(s, errors='coerce').fillna(0).astype(int)

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_60/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    for col in ['N.°', 'Departamento', 'Población cabecera', 'Población resto', 'Población Total']:
        df[col] = clean_int_column(df[col])
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

agg_df = df_all.groupby(['Municipio', 'N.°', 'Departamento'], as_index=False).agg({
    'Población cabecera': 'sum',
    'Población resto': 'sum',
    'Población Total': 'sum'
})

agg_df = agg_df[['Municipio', 'N.°', 'Departamento', 'Población cabecera', 'Población resto', 'Población Total']]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_60/target_multisource_mcts.csv", index=False)