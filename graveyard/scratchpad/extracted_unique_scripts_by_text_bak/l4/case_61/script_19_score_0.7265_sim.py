import pandas as pd

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

df_all = pd.concat(dfs, ignore_index=True)

def clean_int_column(col):
    return col.astype(str).str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '', regex=False).astype(int)

df_all['Población resto'] = df_all['Población resto'].astype(str).str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False)
df_all['Población cabecera'] = df_all['Población cabecera'].astype(str).str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False)
df_all['Población Total'] = df_all['Población Total'].astype(str).str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False)

df_all['Población resto'] = df_all['Población resto'].str.replace('.', '', regex=False).str.replace(',', '', regex=False)
df_all['Población cabecera'] = df_all['Población cabecera'].str.replace('.', '', regex=False).str.replace(',', '', regex=False)
df_all['Población Total'] = df_all['Población Total'].str.replace('.', '', regex=False).str.replace(',', '', regex=False)

df_all['Población resto'] = df_all['Población resto'].astype(int)
df_all['Población cabecera'] = df_all['Población cabecera'].astype(int)
df_all['Población Total'] = df_all['Población Total'].astype(int)

df_all['N.°'] = df_all['N.°'].astype(int)

df_all = df_all[['Población resto', 'N.°', 'Municipio', 'Departamento', 'Población cabecera', 'Población Total']]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_61/target_multisource_mcts.csv", index=False)