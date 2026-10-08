import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_57/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_57/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_57/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_57/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)

df_all = df_all.dropna(subset=['TransTo'])

result = df_all.groupby(['TransTo', 'WarNum'], as_index=False)['TransTo'].sum()
result = result.rename(columns={'TransTo': 'TransTo', 'WarNum': 'WarNum'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_57/target_multisource_mcts.csv", index=False)