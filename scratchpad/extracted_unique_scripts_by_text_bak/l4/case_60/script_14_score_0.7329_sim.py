import pandas as pd

def clean_population_column(col):
    return col.str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False).astype(int)

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_60/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    df['Población cabecera'] = clean_population_column(df['Población cabecera'])
    df['Población resto'] = clean_population_column(df['Población resto'])
    df['Población Total'] = clean_population_column(df['Población Total'])
    df['N.°'] = df['N.°'].astype(int)
    # Departamento column is string in source but target expects integer, but from examples it looks like Departamento is integer in target.
    # However, source Departamento is string (e.g. "Norte de Santander"), target expects integer.
    # So we need to convert Departamento string to integer codes.
    dfs.append(df)

all_data = pd.concat(dfs, ignore_index=True)

# Convert Departamento to categorical codes (integer) to match target schema
all_data['Departamento'] = all_data['Departamento'].astype('category').cat.codes + 1

grouped = all_data.groupby(['Municipio', 'N.°', 'Departamento'], as_index=False).agg({
    'Población cabecera': 'sum',
    'Población resto': 'sum',
    'Población Total': 'sum'
})

grouped['N.°'] = grouped['N.°'].astype(int)
grouped['Población cabecera'] = grouped['Población cabecera'].astype(int)
grouped['Población resto'] = grouped['Población resto'].astype(int)
grouped['Población Total'] = grouped['Población Total'].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_60/target_multisource_mcts.csv", index=False)