import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_79/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_79/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_79/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_79/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length4_79/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

df['hero'] = df['hero'].astype(str)
df['disadvantage'] = df['disadvantage'].astype(float)
df['winrate'] = df['winrate'].astype(float)
df['matches'] = df['matches'].astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_79/target_multisource_mcts.csv", index=False)