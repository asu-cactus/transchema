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
    for col in ['Población cabecera', 'Población resto', 'Población Total']:
        df[col] = df[col].astype(str).str.replace('\xa0', '').str.replace(' ', '').str.replace('.', '').str.replace(',', '').astype(int)
    df['Departamento'] = df['Departamento'].astype(str)
    df['N.°'] = pd.to_numeric(df['N.°'], errors='coerce').fillna(0).astype(int)
    df['Municipio'] = pd.to_numeric(df['Municipio'], errors='coerce').fillna(0).astype(int)
    dfs.append(df)

result = pd.concat(dfs, ignore_index=True)
result = result[['Departamento', 'N.°', 'Municipio', 'Población cabecera', 'Población resto', 'Población Total']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_59/target_multisource_mcts.csv", index=False)