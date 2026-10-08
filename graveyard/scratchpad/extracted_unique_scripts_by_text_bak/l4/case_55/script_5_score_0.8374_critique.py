import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_55/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_55/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_55/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_55/training_3.csv", index_col=0)

# Union all source tables
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Ensure correct types
df_all = df_all.astype({'WarNum': 'int64', 'WhereFought': 'int64'})

# Group by WarNum and aggregate WhereFought by min to remove duplicates
df_result = df_all.groupby('WarNum', as_index=False).agg({'WhereFought': 'min'})

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length4_55/target_multisource_mcts.csv", index=False)