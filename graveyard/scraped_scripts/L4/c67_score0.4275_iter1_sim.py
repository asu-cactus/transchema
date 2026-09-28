import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_67/training_0.csv", index_col=0)

df_joined = pd.merge(df0, df0, left_on='Batsman on strike', right_on='batsman on non-strike', suffixes=('', '_r'))

result = df_joined[['Batsman on strike', 'overs', 'runs scored', 'extras']].copy()

result['Batsman on strike'] = result['Batsman on strike'].astype(str)
result['overs'] = result['overs'].astype(float)
result['runs scored'] = result['runs scored'].astype(int)
result['extras'] = result['extras'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_67/target_multisource_mcts.csv", index=False)