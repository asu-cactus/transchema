import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_54/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_54/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_54/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_54/training_3.csv", index_col=0)

# Union all source tables
union_df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Group by 'WhereFought' and count 'WarNum'
grouped = union_df.groupby('WhereFought', as_index=False).agg({'WarNum': 'count'})

# Rename columns to match target schema ['WhereFought', 'WarNum']
# The count of WarNum per WhereFought is stored in 'WarNum' column already
grouped = grouped[['WhereFought', 'WarNum']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_54/target_multisource_mcts.csv", index=False)