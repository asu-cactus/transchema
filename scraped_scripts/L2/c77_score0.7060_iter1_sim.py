import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_77/training_0.csv", index_col=0)
df = df0[['city', 'driver_count']].copy()
df['city'] = df['city'].astype(str)
df['driver_count'] = pd.to_numeric(df['driver_count'], errors='coerce').fillna(0).astype(int)
df.to_csv("autopipeline-benchmarks/github-pipelines/length2_77/target_multisource_mcts.csv", index=False)