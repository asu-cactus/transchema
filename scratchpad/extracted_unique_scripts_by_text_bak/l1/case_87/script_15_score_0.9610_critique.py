import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_87/training_0.csv", index_col=0)

# If there were multiple source tables, we would read and concat them all here.
# Since only one source table is given, just use df0.

# Ensure correct types
df0['condition'] = df0['condition'].astype(int)
df0['click'] = df0['click'].astype(float)

# Group by 'condition' and aggregate mean of 'click'
result = df0.groupby('condition', as_index=False).agg({'click': 'mean'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_87/target_multisource_mcts.csv", index=False)