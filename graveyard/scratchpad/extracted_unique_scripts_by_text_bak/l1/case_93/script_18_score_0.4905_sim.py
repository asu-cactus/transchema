import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_93/training_0.csv", index_col=0)
df0['bet'] = pd.to_numeric(df0['bet'], errors='coerce')
df0['win'] = pd.to_numeric(df0['win'], errors='coerce')
agg = df0.groupby(['user_id', 'time'], as_index=False).agg({'bet':'sum', 'win':'sum'})
agg['user_id'] = agg['user_id'].astype(str)
agg['time'] = agg['time'].astype(str)
agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_93/target_multisource_mcts.csv", index=False)