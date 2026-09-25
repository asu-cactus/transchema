import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_85/training_0.csv", index_col=0)
df = df0[['crit_cn', 'critic']].copy()
df['critic'] = pd.to_numeric(df['critic'], errors='coerce')
df = df.dropna(subset=['critic'])
df['critic'] = df['critic'].astype(int)
df.to_csv("autopipeline-benchmarks/github-pipelines/length4_85/target_multisource_mcts.csv", index=False)