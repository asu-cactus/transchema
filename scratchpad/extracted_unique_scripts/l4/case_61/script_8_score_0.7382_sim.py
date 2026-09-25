import pandas as pd

def clean_number_column(col):
    return col.str.replace(r'\s+', '', regex=True).str.replace(' ', '', regex=False).str.replace(',', '').astype(int)

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_61/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    df['Población cabecera'] = clean_number_column(df['Población cabecera'])
    df['Población resto'] = clean_number_column(df['Población resto'])
    df['Población Total'] = clean_number_column(df['Población Total'])
    df['N.°'] = df['N.°'].astype(int)
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

agg = df_all.groupby(['N.°', 'Municipio', 'Departamento'], as_index=False).agg({
    'Población cabecera': 'sum',
    'Población resto': 'sum',
    'Población Total': 'sum'
})

agg['Municipio'] = agg['Municipio'].astype(str)
agg['Departamento'] = agg['Departamento'].astype(str)

agg['Población resto'] = agg['Población resto'].map('{:,}'.format).str.replace(',', ' ')
agg['Población cabecera'] = agg['Población cabecera'].map('{:,}'.format).str.replace(',', ' ')
agg['Población Total'] = agg['Población Total'].map('{:,}'.format).str.replace(',', ' ')

agg = agg[['Población resto', 'N.°', 'Municipio', 'Departamento', 'Población cabecera', 'Población Total']]

agg['N.°'] = agg['N.°'].astype(int)
agg['Municipio'] = agg['Municipio'].astype(str)
agg['Departamento'] = agg['Departamento'].astype(str)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_61/target_multisource_mcts.csv", index=False)