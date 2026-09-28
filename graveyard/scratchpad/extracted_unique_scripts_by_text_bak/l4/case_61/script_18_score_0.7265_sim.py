import pandas as pd

def clean_number_column(col):
    return col.str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False).astype(int)

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_61/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df['Población resto'] = clean_number_column(df['Población resto'])
df['Población cabecera'] = clean_number_column(df['Población cabecera'])
df['Población Total'] = clean_number_column(df['Población Total'])
df['N.°'] = df['N.°'].astype(int)

df = df[['Población resto', 'N.°', 'Municipio', 'Departamento', 'Población cabecera', 'Población Total']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_61/target_multisource_mcts.csv", index=False)