import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_65/training_0.csv", index_col=0)

# Group by 'year' and sum 'vote_count'
result = df0.groupby('year', as_index=False)['vote_count'].sum()

# Rename columns to match target schema
result.columns = ['year', '0']

# Ensure correct types
result['year'] = result['year'].astype(int)
result['0'] = result['0'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_65/target_multisource_mcts.csv", index=False)