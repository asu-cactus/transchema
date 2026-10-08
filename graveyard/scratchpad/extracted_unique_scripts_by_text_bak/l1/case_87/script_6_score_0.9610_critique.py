import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_87/training_0.csv", index_col=0)

# Group by 'condition' and compute mean of 'click'
result = df0.groupby('condition', as_index=False)['click'].mean()

# Ensure types match target schema
result['condition'] = result['condition'].astype(int)
result['click'] = result['click'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_87/target_multisource_mcts.csv", index=False)