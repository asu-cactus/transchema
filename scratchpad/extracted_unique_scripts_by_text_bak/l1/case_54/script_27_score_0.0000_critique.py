import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_54/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_54/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_54/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_54/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_54/training_4.csv"
]

# Read all source tables
dfs = [pd.read_csv(p, index_col=0) for p in paths]

# Rename 'click' columns to unique names to avoid collision after join
for i, df in enumerate(dfs):
    df.rename(columns={'click': f'click_{i}'}, inplace=True)

# Perform successive inner joins on 'condition'
from functools import reduce

df_joined = reduce(lambda left, right: pd.merge(left, right, on='condition', how='inner'), dfs)

# Sum all click columns row-wise to get total clicks per condition
click_cols = [f'click_{i}' for i in range(len(dfs))]
df_joined['click'] = df_joined[click_cols].sum(axis=1)

# Select only the target columns
result = df_joined[['condition', 'click']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_54/target_multisource_mcts.csv", index=False)