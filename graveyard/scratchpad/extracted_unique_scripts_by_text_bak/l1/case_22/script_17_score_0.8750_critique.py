import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_22/training_0.csv", index_col=0)

# Group by 'condition' and sum 'click'
result = df.groupby('condition', as_index=False)['click'].sum()

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_22/target_multisource_mcts.csv", index=False)