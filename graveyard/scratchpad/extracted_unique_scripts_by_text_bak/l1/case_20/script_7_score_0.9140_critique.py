import pandas as pd

# Read all source tables (assuming 4 source files as typical for this benchmark)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_20/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_20/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_20/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_20/training_3.csv", index_col=0)

# Union all source tables
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Group by 'sex' and 'smoker' and aggregate mean for numeric columns
result = df_all.groupby(['sex', 'smoker'], as_index=False).agg({
    'total_bill': 'mean',
    'tip': 'mean',
    'size': 'mean'
})

# Write output with exact target schema column names
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_20/target_multisource_mcts.csv", index=False)