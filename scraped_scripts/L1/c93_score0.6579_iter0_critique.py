import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_93/training_0.csv", index_col=0)

# Ensure columns have correct types matching target schema
df0['user_id'] = df0['user_id'].astype(str)
df0['time'] = df0['time'].astype(str)
df0['bet'] = df0['bet'].astype(float)
df0['win'] = df0['win'].astype(float)

df0.to_csv("autopipeline-benchmarks/github-pipelines/length1_93/target_multisource_mcts.csv", index=False)