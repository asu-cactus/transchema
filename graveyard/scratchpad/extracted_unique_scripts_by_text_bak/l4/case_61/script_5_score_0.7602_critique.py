import pandas as pd

def parse_int_str(s):
    if pd.isna(s):
        return 0
    return int(str(s).replace('\xa0','').replace(' ','').replace(',',''))

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_61/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_61/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    # Clean population columns: remove spaces, non-breaking spaces, commas, convert to int
    for col in ['Población cabecera', 'Población resto', 'Población Total']:
        df[col] = df[col].astype(str).str.replace('\xa0','').str.replace(' ','').str.replace(',','')
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    dfs.append(df)

# UNION all source tables
union_df = pd.concat(dfs, ignore_index=True)

# Convert 'Municipio' and 'Departamento' to integer codes to match target schema
# 'N.°' is already integer in source, just ensure type
union_df['N.°'] = pd.to_numeric(union_df['N.°'], errors='coerce').fillna(0).astype(int)

# Map 'Municipio' strings to integer codes starting from 1
municipio_codes = {name: i+1 for i, name in enumerate(sorted(union_df['Municipio'].unique()))}
union_df['Municipio'] = union_df['Municipio'].map(municipio_codes)

# Map 'Departamento' strings to integer codes starting from 1
departamento_codes = {name: i+1 for i, name in enumerate(sorted(union_df['Departamento'].unique()))}
union_df['Departamento'] = union_df['Departamento'].map(departamento_codes)

# Group by the leftmost integer columns in target schema: ['N.°', 'Municipio', 'Departamento']
grouped = union_df.groupby(['N.°', 'Municipio', 'Departamento'], as_index=False).agg({
    'Población cabecera': 'sum',
    'Población resto': 'sum',
    'Población Total': 'sum'
})

# Convert 'Población resto' back to string with thousands separator (space)
grouped['Población resto'] = grouped['Población resto'].apply(lambda x: f"{x:,}".replace(',', ' '))

# Reorder columns exactly as target schema
result = grouped[['Población resto', 'N.°', 'Municipio', 'Departamento', 'Población cabecera', 'Población Total']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_61/target_multisource_mcts.csv", index=False)