import pandas as pd

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
        df[col] = df[col].astype(str).str.replace('\xa0', '').str.replace(' ', '').str.replace('.', '').str.replace(',', '').astype(int)
    df['Departamento'] = df['Departamento'].astype('category').cat.codes + 1
    df['Municipio'] = df['Municipio'].astype('category').cat.codes + 1
    dfs.append(df)

result = pd.concat(dfs, ignore_index=True)

result = result.astype({
    'Población cabecera': 'int',
    'Población resto': 'int',
    'Población Total': 'int',
    'N.°': 'int',
    'Municipio': 'int',
    'Departamento': 'int'
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_61/target_multisource_mcts.csv", index=False)