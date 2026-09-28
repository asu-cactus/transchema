import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length2_34/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length2_34/training_1.csv', index_col=0)

df = df1[['city', 'ride_id']].copy()
df['ride_id'] = pd.to_numeric(df['ride_id'], errors='coerce').astype('Int64')

df.to_csv('autopipeline-benchmarks/github-pipelines/length2_34/target_multisource_mcts.csv', index=False)