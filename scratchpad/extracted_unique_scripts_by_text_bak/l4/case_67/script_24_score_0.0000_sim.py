import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_67/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, left_on=['overs', 'Batsman on strike'], right_on=['overs', 'bowler'], suffixes=('', '_r'))

agg = joined.groupby('Batsman on strike').agg({
    'runs scored': 'sum',
    'extras': 'sum',
    'overs': 'max'
}).reset_index()

agg = agg.rename(columns={
    'Batsman on strike': 'Batsman on strike',
    'runs scored': 'runs scored',
    'extras': 'extras',
    'overs': 'overs'
})

agg['overs'] = agg['overs'].astype(float)
agg['runs scored'] = agg['runs scored'].astype(int)
agg['extras'] = agg['extras'].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_67/target_multisource_mcts.csv", index=False)