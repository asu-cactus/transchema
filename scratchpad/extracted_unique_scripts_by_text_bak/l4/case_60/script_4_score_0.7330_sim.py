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
    df['Departamento'] = df['Departamento'].astype(str)
    df['Municipio'] = df['Municipio'].astype(str)
    df['N.°'] = df['N.°'].astype(int)
    dfs.append(df)

result = pd.concat(dfs, ignore_index=True)

result = result[['Municipio', 'N.°', 'Departamento', 'Población cabecera', 'Población resto', 'Población Total']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_60/target_multisource_mcts.csv", index=False)