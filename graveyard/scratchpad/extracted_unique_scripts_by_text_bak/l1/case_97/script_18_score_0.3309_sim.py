import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_97/training_0.csv", index_col=0)
df0 = df0[['crit_cn', 'critic']].copy()
df0['critic'] = pd.to_numeric(df0['critic'], errors='coerce').astype('Int64')
df0.to_csv("autopipeline-benchmarks/github-pipelines/length1_97/target_multisource_mcts.csv", index=False)