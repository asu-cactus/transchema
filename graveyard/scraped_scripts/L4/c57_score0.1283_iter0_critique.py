import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_3.csv", index_col=0)

# Union all source tables
df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Drop duplicates to get unique pairs
df = df.drop_duplicates()

# Reorder columns to match target schema ['TransTo', 'WarNum']
result = df[['TransTo', 'WarNum']]

# Convert to integer type (nullable Int64 to handle NaNs if any)
result = result.astype({'TransTo': 'Int64', 'WarNum': 'Int64'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_57/target_multisource_mcts.csv", index=False)