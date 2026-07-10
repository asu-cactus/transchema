import pandas as pd

def clean_int_column(s):
    return pd.to_numeric(s.str.replace(r'\s', '', regex=True), errors='coerce').fillna(0).astype(int)

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_60/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_60/training_3.csv"
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    df['Población cabecera'] = clean_int_column(df['Población cabecera'])
    df['Población resto'] = clean_int_column(df['Población resto'])
    df['Población Total'] = clean_int_column(df['Población Total'])
    df['Departamento'] = df['Departamento'].astype(str).str.strip()
    df['Municipio'] = df['Municipio'].astype(str).str.strip()
    df['N.°'] = pd.to_numeric(df['N.°'], errors='coerce').fillna(0).astype(int)
    dfs.append(df)

result = pd.concat(dfs, ignore_index=True)

# Map Departamento to integer codes to match target schema type
dept_codes = {dept: i+1 for i, dept in enumerate(sorted(result['Departamento'].unique()))}
result['Departamento'] = result['Departamento'].map(dept_codes).fillna(0).astype(int)

result = result[['Municipio', 'N.°', 'Departamento', 'Población cabecera', 'Población resto', 'Población Total']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_60/target_multisource_mcts.csv", index=False)