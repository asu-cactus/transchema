import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_93/training_0.csv", index_col=0)

agg = df0.groupby(['time', 'user_id'], as_index=False).agg({'bet':'min', 'win':'min'})

agg = agg.rename(columns={'user_id':'user_id', 'time':'time', 'bet':'bet', 'win':'win'})

agg['user_id'] = agg['user_id'].astype(str)
agg['time'] = agg['time'].astype(str)
agg['bet'] = agg['bet'].astype(float)
agg['win'] = agg['win'].astype(float)

agg = agg[['user_id', 'time', 'bet', 'win']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_93/target_multisource_mcts.csv", index=False)