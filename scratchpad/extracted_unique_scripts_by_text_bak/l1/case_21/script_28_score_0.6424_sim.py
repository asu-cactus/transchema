import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_21/training_0.csv", index_col=0)

# The JOIN of the same table on Major_category is effectively a no-op here, so we just use df0 directly.
# We need to produce a table with columns ['Major_category', 'Median'].
# Median is already present as a float column in df0.
result = df0[['Major_category', 'Median']].copy()

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_21/target_multisource_mcts.csv", index=False)