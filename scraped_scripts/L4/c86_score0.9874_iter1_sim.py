import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_86/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_86/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_86/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_86/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length4_86/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df['precio'] = pd.to_numeric(df['precio'], errors='coerce')

df = df.astype({
    'titulo': 'string',
    'tipo': 'string',
    'condicion': 'string',
    'ubicacion': 'string',
    'tiempo': 'string',
    'reputacion': 'string',
    'pago': 'string'
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_86/target_multisource_mcts.csv", index=False)