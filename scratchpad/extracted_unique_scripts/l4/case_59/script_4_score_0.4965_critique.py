import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_59/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    # Clean numeric columns: remove spaces, non-breaking spaces, dots, commas
    for col in ['Población cabecera', 'Población resto', 'Población Total']:
        df[col] = df[col].astype(str).str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '', regex=False).astype(int)
    # Departamento as string
    df['Departamento'] = df['Departamento'].astype(str)
    # N.° as integer
    df['N.°'] = pd.to_numeric(df['N.°'], errors='coerce').fillna(0).astype(int)
    # Municipio is string, keep as string for now
    df['Municipio'] = df['Municipio'].astype(str)
    dfs.append(df)

# Concatenate all sources
all_data = pd.concat(dfs, ignore_index=True)

# Create consistent Municipio integer IDs across all data
# Map Municipio string to integer IDs starting from 1
municipio_unique = all_data['Municipio'].unique()
municipio_id_map = {name: idx+1 for idx, name in enumerate(sorted(municipio_unique))}
all_data['Municipio'] = all_data['Municipio'].map(municipio_id_map).astype(int)

# Group by Departamento, N.°, Municipio and sum population columns
result = all_data.groupby(['Departamento', 'N.°', 'Municipio'], as_index=False).agg({
    'Población cabecera': 'sum',
    'Población resto': 'sum',
    'Población Total': 'sum'
})

# Ensure column order and types as target schema
result = result[['Departamento', 'N.°', 'Municipio', 'Población cabecera', 'Población resto', 'Población Total']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_59/target_multisource_mcts.csv", index=False)