import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_93/training_0.csv", index_col=0)

agg = df0.groupby(['user_id', 'time'], as_index=False).agg({'bet':'count', 'win':'count'})

agg.rename(columns={'bet':'bet', 'win':'win'}, inplace=True)

agg['user_id'] = agg['user_id'].astype(str)
agg['time'] = agg['time'].astype(str)
agg['bet'] = agg['bet'].astype(float)
agg['win'] = agg['win'].astype(float)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_93/target_multisource_mcts.csv", index=False)