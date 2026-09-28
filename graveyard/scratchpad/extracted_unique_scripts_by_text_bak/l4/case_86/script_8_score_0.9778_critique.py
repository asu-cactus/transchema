import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_86/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_86/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_86/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_86/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length4_86/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

# Convert 'precio' to numeric safely in each dataframe before concatenation
for i in range(len(dfs)):
    dfs[i]['precio'] = pd.to_numeric(dfs[i]['precio'], errors='coerce')

df = pd.concat(dfs, ignore_index=True)

# Ensure columns are exactly as target schema
df = df[['titulo', 'tipo', 'precio', 'condicion', 'ubicacion', 'tiempo', 'reputacion', 'pago']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_86/target_multisource_mcts.csv", index=False)