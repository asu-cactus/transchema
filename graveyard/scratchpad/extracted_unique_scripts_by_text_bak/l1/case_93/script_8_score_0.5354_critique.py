import pandas as pd

source_path = "autopipeline-benchmarks/github-pipelines/length1_93/training_0.csv"
df = pd.read_csv(source_path, index_col=0)

# Ensure columns have correct types matching target schema
df['user_id'] = df['user_id'].astype(str)
df['time'] = df['time'].astype(str)
df['bet'] = df['bet'].astype(float)
df['win'] = df['win'].astype(float)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_93/target_multisource_mcts.csv", index=False)