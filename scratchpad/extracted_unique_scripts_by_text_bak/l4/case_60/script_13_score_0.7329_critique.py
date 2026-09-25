import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_60/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_3.csv",
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    for col in ['Población cabecera', 'Población resto', 'Población Total']:
        df[col] = df[col].astype(str).str.replace('\xa0', '').str.replace(' ', '').astype(int)
    df['Municipio'] = df['Municipio'].astype(str)
    df['N.°'] = df['N.°'].astype(int)
    df['Departamento'] = df['Departamento'].astype(str)
    dfs.append(df)

# Concatenate all source tables (UNION)
result = pd.concat(dfs, ignore_index=True)

# Map 'Departamento' strings to unique integers
departamento_unique = result['Departamento'].unique()
departamento_map = {name: idx+1 for idx, name in enumerate(sorted(departamento_unique))}
result['Departamento'] = result['Departamento'].map(departamento_map).astype(int)

# Group by key columns and sum population columns to remove duplicates and aggregate
result = result.groupby(['Municipio', 'N.°', 'Departamento'], as_index=False).agg({
    'Población cabecera': 'sum',
    'Población resto': 'sum',
    'Población Total': 'sum'
})

# Reorder columns to match target schema
result = result[['Municipio', 'N.°', 'Departamento', 'Población cabecera', 'Población resto', 'Población Total']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_60/target_multisource_mcts.csv", index=False)