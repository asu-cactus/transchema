import pandas as pd

def clean_int_column(s):
    if s.dtype == object:
        s = s.str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False)
    return pd.to_numeric(s, errors='coerce').fillna(0).astype(int)

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

df_all['Población resto'] = df_all['Población resto'].astype(str).str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False)
df_all['Población resto'] = pd.to_numeric(df_all['Población resto'], errors='coerce').fillna(0).astype(int)

df_all['Población cabecera'] = df_all['Población cabecera'].astype(str).str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False)
df_all['Población cabecera'] = pd.to_numeric(df_all['Población cabecera'], errors='coerce').fillna(0).astype(int)

df_all['Población Total'] = df_all['Población Total'].astype(str).str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False)
df_all['Población Total'] = pd.to_numeric(df_all['Población Total'], errors='coerce').fillna(0).astype(int)

df_all['N.°'] = pd.to_numeric(df_all['N.°'], errors='coerce').fillna(0).astype(int)

df_all['Municipio'] = pd.to_numeric(df_all['Municipio'], errors='coerce')
if df_all['Municipio'].isnull().all():
    # Municipio is string, convert to categorical codes starting at 1
    df_all['Municipio'] = df_all['Municipio'].astype(str).str.strip()
    df_all['Municipio'] = df_all['Municipio'].astype('category').cat.codes + 1
else:
    df_all['Municipio'] = df_all['Municipio'].fillna(0).astype(int)

df_all['Departamento'] = pd.to_numeric(df_all['Departamento'], errors='coerce')
if df_all['Departamento'].isnull().all():
    df_all['Departamento'] = df_all['Departamento'].astype(str).str.strip()
    df_all['Departamento'] = df_all['Departamento'].astype('category').cat.codes + 1
else:
    df_all['Departamento'] = df_all['Departamento'].fillna(0).astype(int)

df_all = df_all[['Población resto', 'N.°', 'Municipio', 'Departamento', 'Población cabecera', 'Población Total']]

df_all['Población resto'] = df_all['Población resto'].astype(str)

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_61/target_multisource_mcts.csv", index=False)