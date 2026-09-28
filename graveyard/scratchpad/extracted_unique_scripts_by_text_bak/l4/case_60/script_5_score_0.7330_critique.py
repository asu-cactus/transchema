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
    dfs.append(df)

# UNION all source tables by concatenation
all_data = pd.concat(dfs, ignore_index=True)

# Convert Departamento to categorical codes (integer) to match target schema
all_data['Departamento'] = all_data['Departamento'].astype('category').cat.codes + 1

# Reorder columns to match target schema exactly
all_data = all_data[['Municipio', 'N.°', 'Departamento', 'Población cabecera', 'Población resto', 'Población Total']]

# Ensure correct dtypes
all_data['N.°'] = all_data['N.°'].astype(int)
all_data['Departamento'] = all_data['Departamento'].astype(int)
all_data['Población cabecera'] = all_data['Población cabecera'].astype(int)
all_data['Población resto'] = all_data['Población resto'].astype(int)
all_data['Población Total'] = all_data['Población Total'].astype(int)

all_data.to_csv("autopipeline-benchmarks/github-pipelines/length4_60/target_multisource_mcts.csv", index=False)