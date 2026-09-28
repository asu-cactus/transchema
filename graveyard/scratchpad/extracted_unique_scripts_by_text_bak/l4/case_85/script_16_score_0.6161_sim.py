import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_85/training_0.csv", index_col=0)
df0['critic'] = pd.to_numeric(df0['critic'], errors='coerce').fillna(0).astype(int)
result = df0.groupby('crit_cn', as_index=False)['critic'].sum()
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_85/target_multisource_mcts.csv", index=False)