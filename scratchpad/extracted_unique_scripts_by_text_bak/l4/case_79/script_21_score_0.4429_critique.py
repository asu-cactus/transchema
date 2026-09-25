import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_4.csv", index_col=0)

union_all = pd.concat([s0, s1, s2, s3, s4], ignore_index=True)

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