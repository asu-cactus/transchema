import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_4.csv", index_col=0)

join_result = pd.merge(s2, s3, on="hero", suffixes=('_2', '_3'))

join_result = join_result.assign(
    disadvantage = (join_result['disadvantage_2'] + join_result['disadvantage_3']) / 2,
    winrate = (join_result['winrate_2'] + join_result['winrate_3']) / 2,
    matches = join_result['matches_2'] + join_result['matches_3']
)[['hero', 'disadvantage', 'winrate', 'matches']]

union_all = pd.concat([s0, s1, s4, join_result], ignore_index=True)

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