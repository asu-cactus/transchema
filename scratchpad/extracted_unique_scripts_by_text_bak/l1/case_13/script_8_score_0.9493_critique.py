import pandas as pd

# Read the single source table (if more, read all and concat)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_13/training_0.csv", index_col=0)

# If multiple source tables existed, union them here:
# df = pd.concat([df0, df1, df2, ...], ignore_index=True)
df = df0

# Group by 'sex' and 'smoker' and aggregate average tip_pct
result = df.groupby(['sex', 'smoker'], as_index=False)['tip_pct'].mean()

# Write output with exact column names as target schema
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_13/target_multisource_mcts.csv", index=False)