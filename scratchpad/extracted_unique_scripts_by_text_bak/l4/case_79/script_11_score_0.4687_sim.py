import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_4.csv", index_col=0)

join_0 = pd.merge(s2, s3, on="hero", suffixes=('_2', '_3'))
join_0 = join_0.assign(
    disadvantage = join_0['disadvantage_2'],
    winrate = join_0['winrate_2'],
    matches = join_0['matches_2']
)[['hero', 'disadvantage', 'winrate', 'matches']]

join_1 = pd.merge(s0, s1, on="hero", suffixes=('_0', '_1'))
join_1 = join_1.assign(
    disadvantage = join_1['disadvantage_0'],
    winrate = join_1['winrate_0'],
    matches = join_1['matches_0']
)[['hero', 'disadvantage', 'winrate', 'matches']]

union_all = pd.concat([join_0, join_1, s4], ignore_index=True)

agg = union_all.groupby('hero', as_index=False).agg({
    'disadvantage': 'mean',
    'winrate': 'mean',
    'matches': 'sum'
})

agg['hero'] = agg['hero'].astype(str)
agg['disadvantage'] = agg['disadvantage'].astype(float)
agg['winrate'] = agg['winrate'].astype(float)
agg['matches'] = agg['matches'].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_79/target_multisource_mcts.csv", index=False)