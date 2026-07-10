import pandas as pd

def clean_population_column(col):
    return col.str.replace('\xa0', '').str.replace(' ', '').astype(int)

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_60/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df['Población cabecera'] = clean_population_column(df['Población cabecera'])
df['Población resto'] = clean_population_column(df['Población resto'])
df['Población Total'] = clean_population_column(df['Población Total'])
df['N.°'] = df['N.°'].astype(int)

# Convert 'Departamento' string to integer codes to match target schema
df['Departamento'] = pd.factorize(df['Departamento'])[0] + 1  # +1 to start codes at 1

df = df[['Municipio', 'N.°', 'Departamento', 'Población cabecera', 'Población resto', 'Población Total']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_60/target_multisource_mcts.csv", index=False)