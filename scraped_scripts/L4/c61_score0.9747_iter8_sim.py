import pandas as pd

def clean_number_column(col):
    return col.str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False).astype(int)

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_61/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    df['Población resto'] = df['Población resto'].astype(str)
    df['Población cabecera'] = df['Población cabecera'].astype(str)
    df['Población Total'] = df['Población Total'].astype(str)
    df['Población resto'] = df['Población resto'].str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False)
    df['Población cabecera'] = df['Población cabecera'].str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False)
    df['Población Total'] = df['Población Total'].str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False)
    df['Población resto'] = df['Población resto'].astype(str)
    df['Población cabecera'] = df['Población cabecera'].astype(str)
    df['Población Total'] = df['Población Total'].astype(str)
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

df_all['N.°'] = pd.to_numeric(df_all['N.°'], errors='coerce').fillna(0).astype(int)
df_all['Municipio'] = pd.to_numeric(df_all['Municipio'], errors='coerce').fillna(0).astype(int)
df_all['Departamento'] = pd.to_numeric(df_all['Departamento'], errors='coerce').fillna(0).astype(int)

df_all['Población cabecera'] = df_all['Población cabecera'].astype(str).str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False)
df_all['Población cabecera'] = pd.to_numeric(df_all['Población cabecera'], errors='coerce').fillna(0).astype(int)

df_all['Población Total'] = df_all['Población Total'].astype(str).str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False)
df_all['Población Total'] = pd.to_numeric(df_all['Población Total'], errors='coerce').fillna(0).astype(int)

df_all['Población resto'] = df_all['Población resto'].astype(str)

grouped = df_all.groupby('Población resto', dropna=False).agg(
    **{
        'N.°': ('N.°', 'count'),
        'Población cabecera': ('Población cabecera', 'sum'),
        'Población Total': ('Población Total', 'sum')
    }
).reset_index()

grouped['Municipio'] = 1
grouped['Departamento'] = 1

grouped = grouped[['Población resto', 'N.°', 'Municipio', 'Departamento', 'Población cabecera', 'Población Total']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_61/target_multisource_mcts.csv", index=False)