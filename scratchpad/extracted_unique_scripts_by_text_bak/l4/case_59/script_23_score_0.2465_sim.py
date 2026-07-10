import pandas as pd
import numpy as np

def clean_population_column(col):
    return col.astype(str).str.replace(r'\s', '', regex=True).str.replace(' ', '', regex=False).str.replace(',', '').astype(float)

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_59/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    df['Población cabecera'] = clean_population_column(df['Población cabecera'])
    df['Población resto'] = clean_population_column(df['Población resto'])
    df['Población Total'] = clean_population_column(df['Población Total'])
    df['N.°'] = pd.to_numeric(df['N.°'], errors='coerce').astype('Int64')
    df['Municipio'] = pd.to_numeric(df['Municipio'], errors='coerce').astype('Int64')
    df['Departamento'] = df['Departamento'].astype(str)
    dfs.append(df)

union_df = pd.concat(dfs, ignore_index=True)

agg_df = union_df.groupby(['Departamento', 'N.°', 'Municipio'], dropna=False).agg({
    'Población cabecera': 'mean',
    'Población resto': 'mean',
    'Población Total': 'mean'
}).reset_index()

agg_df['Población cabecera'] = agg_df['Población cabecera'].round().astype('Int64')
agg_df['Población resto'] = agg_df['Población resto'].round().astype('Int64')
agg_df['Población Total'] = agg_df['Población Total'].round().astype('Int64')

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_59/target_multisource_mcts.csv", index=False)