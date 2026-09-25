import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_97/training_0.csv", index_col=0)

result = df0[['crit_cn', 'critic']].copy()
result['critic'] = pd.to_numeric(result['critic'], errors='coerce').astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_97/target_multisource_mcts.csv", index=False)