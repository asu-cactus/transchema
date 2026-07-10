import pandas as pd

# Read all source tables (assuming 3 source tables as an example)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_13/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_13/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_13/training_2.csv", index_col=0)

# Union all source tables
df_all = pd.concat([df0, df1, df2], ignore_index=True)

# Group by 'sex' and 'smoker' and aggregate sum of 'tip' and 'total_bill'
grouped = df_all.groupby(['sex', 'smoker'], as_index=False).agg({'tip': 'sum', 'total_bill': 'sum'})

# Compute tip_pct as sum(tip) / sum(total_bill)
grouped['tip_pct'] = grouped['tip'] / grouped['total_bill']

# Select final columns as per target schema
result = grouped[['sex', 'smoker', 'tip_pct']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_13/target_multisource_mcts.csv", index=False)