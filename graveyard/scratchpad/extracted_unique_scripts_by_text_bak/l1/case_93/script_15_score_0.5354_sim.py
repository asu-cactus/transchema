import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_93/training_0.csv", index_col=0)
df = pd.concat([df0], ignore_index=True)
df['user_id'] = df['user_id'].astype(str)
df['time'] = df['time'].astype(str)
df['bet'] = pd.to_numeric(df['bet'], errors='coerce')
df['win'] = pd.to_numeric(df['win'], errors='coerce')
df.to_csv("autopipeline-benchmarks/github-pipelines/length1_93/target_multisource_mcts.csv", index=False)