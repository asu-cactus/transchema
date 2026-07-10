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

# Define aggregation functions
agg_dict = {
    'precio': 'mean',
    'condicion': 'first',
    'ubicacion': 'first',
    'tiempo': 'first',
    'reputacion': 'first',
    'pago': 'first'
}

df = df.groupby(['titulo', 'tipo'], as_index=False).agg(agg_dict)

# Reorder columns to match target schema exactly
df = df[['titulo', 'tipo', 'precio', 'condicion', 'ubicacion', 'tiempo', 'reputacion', 'pago']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_86/target_multisource_mcts.csv", index=False)