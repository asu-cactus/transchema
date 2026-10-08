import pandas as pd

def clean_number_column(col):
    return col.str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False).astype(int)

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_59/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    df['Población cabecera'] = clean_number_column(df['Población cabecera'])
    df['Población resto'] = clean_number_column(df['Población resto'])
    df['Población Total'] = clean_number_column(df['Población Total'])
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

agg = df_all.groupby('Departamento').agg(
    N_=('N.°', 'count'),
    Población_cabecera=('Población cabecera', 'sum'),
    Población_resto=('Población resto', 'sum'),
    Población_Total=('Población Total', 'sum')
).reset_index()

agg = agg.rename(columns={
    'N_': 'N.°',
    'Población_cabecera': 'Población cabecera',
    'Población_resto': 'Población resto',
    'Población_Total': 'Población Total'
})

agg['Municipio'] = agg['N.°']

agg = agg[['Departamento', 'N.°', 'Municipio', 'Población cabecera', 'Población resto', 'Población Total']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_59/target_multisource_mcts.csv", index=False)