import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_67/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, left_on=["overs", "Batsman on strike"], right_on=["overs", "batsman on non-strike"], suffixes=('', '_r'))

grouped = joined.groupby(['Batsman on strike', 'overs'], as_index=False).agg({'runs scored': 'sum', 'extras': 'sum'})

grouped['overs'] = grouped['overs'].astype(float)
grouped['runs scored'] = grouped['runs scored'].astype(int)
grouped['extras'] = grouped['extras'].astype(int)

grouped.rename(columns={'Batsman on strike': 'Batsman on strike'}, inplace=True)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_67/target_multisource_mcts.csv", index=False)