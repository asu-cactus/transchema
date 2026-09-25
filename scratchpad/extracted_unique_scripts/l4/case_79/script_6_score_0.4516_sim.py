import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_4.csv", index_col=0)

join_23 = pd.merge(s2, s3, on="hero", suffixes=('_2', '_3'))

union_all = pd.concat([
    s0,
    s1,
    join_23.rename(columns={
        'disadvantage_2': 'disadvantage',
        'winrate_2': 'winrate',
        'matches_2': 'matches'
    })[['hero', 'disadvantage', 'winrate', 'matches']],
    s4
], ignore_index=True)

grouped = union_all.groupby('hero', as_index=False).agg({
    'disadvantage': 'mean',
    'winrate': 'mean',
    'matches': 'sum'
})

grouped['hero'] = grouped['hero'].astype(str)
grouped['disadvantage'] = grouped['disadvantage'].astype(float)
grouped['winrate'] = grouped['winrate'].astype(float)
grouped['matches'] = grouped['matches'].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_79/target_multisource_mcts.csv", index=False)