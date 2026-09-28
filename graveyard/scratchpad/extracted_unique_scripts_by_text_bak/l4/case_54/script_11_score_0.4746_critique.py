import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_54/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_54/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_54/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_54/training_3.csv", index_col=0)

# Concatenate all source tables (UNION)
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Drop duplicate rows to match target unique pairs
df_all = df_all.drop_duplicates()

# Ensure correct column order as per target schema
df_all = df_all[['WhereFought', 'WarNum']]

# Ensure integer types as in target schema
df_all['WhereFought'] = df_all['WhereFought'].astype(int)
df_all['WarNum'] = df_all['WarNum'].astype(int)

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_54/target_multisource_mcts.csv", index=False)