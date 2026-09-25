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
    for col in ['Población cabecera', 'Población resto', 'Población Total']:
        df[col] = df[col].astype(str).str.replace('\xa0','').str.replace(' ','').str.replace(',','')
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    dfs.append(df)

union_df = pd.concat(dfs, ignore_index=True)

grouped = union_df.groupby('Departamento', as_index=False).agg({
    'Población cabecera': 'sum',
    'Población resto': 'sum',
    'Población Total': 'sum',
    'Municipio': 'count'
})

grouped = grouped.rename(columns={'Municipio': 'N.°'})

grouped['Departamento'] = grouped['Departamento'].astype(int, errors='ignore')
# The target schema says Departamento is integer, but source Departamento is string (names).
# We must convert Departamento to integer. Since source Departamento is string, we assign integer codes.

# Map Departamento strings to integer codes starting from 1
dept_codes = {dept: i+1 for i, dept in enumerate(sorted(grouped['Departamento'].unique()))}
grouped['Departamento'] = grouped['Departamento'].map(dept_codes)

# Convert 'N.°' to int
grouped['N.°'] = grouped['N.°'].astype(int)

# Convert all population columns to int (already done)
grouped['Población cabecera'] = grouped['Población cabecera'].astype(int)
grouped['Población resto'] = grouped['Población resto'].astype(int)
grouped['Población Total'] = grouped['Población Total'].astype(int)

# Reorder columns to match target schema
result = grouped[['Población resto', 'N.°', 'Departamento', 'Población cabecera', 'Población Total']]

# The target schema has 'Municipio' as integer column, but after aggregation Municipio was counted as 'N.°'.
# The target schema columns are:
# ['Población resto': string, 'N.°': integer, 'Municipio': integer, 'Departamento': integer, 'Población cabecera': integer, 'Población Total': integer]
# We have no direct Municipio count column except 'N.°' which is count of Municipio.
# So we add 'Municipio' column equal to 'N.°' (count of Municipio)
result['Municipio'] = result['N.°']

# 'Población resto' is string in target schema, so convert it to string with thousands separator (space)
result['Población resto'] = result['Población resto'].apply(lambda x: f"{x:,}".replace(',', ' '))

# Reorder columns exactly as target schema
result = result[['Población resto', 'N.°', 'Municipio', 'Departamento', 'Población cabecera', 'Población Total']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_61/target_multisource_mcts.csv", index=False)