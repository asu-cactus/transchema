import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_67/training_0.csv", index_col=0)

grouped = df0.groupby('Batsman on strike').agg(
    overs_count=('overs', 'count'),
    runs_avg=('runs scored', 'mean'),
    extras_avg=('extras', 'mean')
).reset_index()

grouped['overs'] = grouped['overs_count'].astype(float)
grouped['runs scored'] = grouped['runs_avg'].round().astype(int)
grouped['extras'] = grouped['extras_avg'].round().astype(int)

result = grouped[['Batsman on strike', 'overs', 'runs scored', 'extras']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_67/target_multisource_mcts.csv", index=False)