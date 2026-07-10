import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_77/training_0.csv', index_col=0)

result = df0[['fac_type', 'capacity']].copy()
result['capacity'] = result['capacity'].astype(int)

result.to_csv('autopipeline-benchmarks/github-pipelines/length1_77/target_multisource_mcts.csv', index=False)