import pandas as pd

def clean_number_column(s):
    return pd.to_numeric(s.str.replace(r'\s', '', regex=True).str.replace(r'\.', '', regex=True), errors='coerce')

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_61/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    dfs.append(df)

union_df = pd.concat(dfs, ignore_index=True)

for col in ['Población cabecera', 'Población resto', 'Población Total']:
    union_df[col] = clean_number_column(union_df[col])

grouped = union_df.groupby('Departamento').agg(
    **{
        'Población cabecera': ('Población cabecera', 'sum'),
        'Población resto': ('Población resto', 'sum'),
        'Población Total': ('Población Total', 'sum'),
        'Municipio': ('Municipio', 'count'),
    }
).reset_index()

grouped['Departamento'] = grouped['Departamento'].astype('int64', errors='ignore')
grouped['Municipio'] = grouped['Municipio'].astype('int64')
grouped['Población cabecera'] = grouped['Población cabecera'].astype('int64')
grouped['Población resto'] = grouped['Población resto'].astype('int64')
grouped['Población Total'] = grouped['Población Total'].astype('int64')

grouped = grouped.rename(columns={
    'Municipio': 'Municipio',
    'Departamento': 'Departamento',
    'Población cabecera': 'Población cabecera',
    'Población resto': 'Población resto',
    'Población Total': 'Población Total'
})

grouped = grouped[['Población resto', 'Municipio', 'Municipio', 'Departamento', 'Población cabecera', 'Población Total']]
grouped = grouped.rename(columns={'Municipio': 'N.°'})
grouped = grouped.rename(columns={'Municipio': 'Municipio'})

grouped = grouped[['Población resto', 'N.°', 'Municipio', 'Departamento', 'Población cabecera', 'Población Total']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_61/target_multisource_mcts.csv", index=False)