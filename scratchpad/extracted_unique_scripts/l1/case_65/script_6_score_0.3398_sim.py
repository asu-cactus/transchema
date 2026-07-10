import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_65/training_0.csv", index_col=0)
result = df0[['year', 'vote_count']].copy()
result.columns = ['year', '0']
result['year'] = result['year'].astype(int)
result['0'] = result['0'].astype(int)
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_65/target_multisource_mcts.csv", index=False)