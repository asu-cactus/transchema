import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_24/training_0.csv', index_col=0)

df = df0[['condition', 'click']].copy()
df['condition'] = df['condition'].astype(int)
df['click'] = df['click'].astype(int)

df.to_csv('autopipeline-benchmarks/github-pipelines/length1_24/target_multisource_mcts.csv', index=False)