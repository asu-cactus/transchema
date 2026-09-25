import pandas as pd
import numpy as np

def clean_number_column(col):
    return col.astype(str).str.replace(r'\s', '', regex=True).str.replace(' ', '', regex=False).str.replace(',', '').str.replace('.', '').replace('', np.nan)

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_60/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    for col in ['Población cabecera', 'Población resto', 'Población Total']:
        df[col] = clean_number_column(df[col])
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df['N.°'] = pd.to_numeric(df['N.°'], errors='coerce')
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

grouped = df_all.groupby(['Municipio', 'N.°', 'Departamento'], dropna=False).agg(
    count_N = ('N.°', 'count'),
    avg_cabecera = ('Población cabecera', 'mean'),
    avg_resto = ('Población resto', 'mean'),
    avg_total = ('Población Total', 'mean')
).reset_index()

result = grouped.rename(columns={
    'count_N': 'N.°',
    'avg_cabecera': 'Población cabecera',
    'avg_resto': 'Población resto',
    'avg_total': 'Población Total'
})

result['N.°'] = result['N.°'].round().astype('Int64')
result['Población cabecera'] = result['Población cabecera'].round().astype('Int64')
result['Población resto'] = result['Población resto'].round().astype('Int64')
result['Población Total'] = result['Población Total'].round().astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_60/target_multisource_mcts.csv", index=False)