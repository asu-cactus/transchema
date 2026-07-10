import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_79/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_79/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_79/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_79/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length4_79/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

result = df_all.groupby('hero', as_index=False).agg({
    'disadvantage': 'mean',
    'winrate': 'mean',
    'matches': 'sum'
})

result['hero'] = result['hero'].astype(str)
result['disadvantage'] = result['disadvantage'].astype(float)
result['winrate'] = result['winrate'].astype(float)
result['matches'] = result['matches'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_79/target_multisource_mcts.csv", index=False)