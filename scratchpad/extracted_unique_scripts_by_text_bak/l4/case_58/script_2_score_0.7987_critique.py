import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_58/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_58/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_58/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_58/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

# Replace NaN in TransTo with 0 as target examples show integer 0, not NaN
df['TransTo'] = df['TransTo'].fillna(0).astype(int)

# Group by WarNum and aggregate TransTo by min (all values are 0 after fillna)
df = df.groupby('WarNum', as_index=False).agg({'TransTo': 'min'})

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_58/target_multisource_mcts.csv", index=False)