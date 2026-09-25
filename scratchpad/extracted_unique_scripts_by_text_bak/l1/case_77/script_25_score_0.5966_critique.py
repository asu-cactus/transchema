import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_77/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_77/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_77/training_2.csv", index_col=0)

# Concatenate all source tables (UNION)
df_all = pd.concat([df0, df1, df2], ignore_index=True)

# Ensure correct types
df_all['fac_type'] = df_all['fac_type'].astype(str)
df_all['capacity'] = pd.to_numeric(df_all['capacity'], errors='coerce').fillna(0).astype(int)

# Group by fac_type and sum capacity
result = df_all.groupby('fac_type', as_index=False)['capacity'].sum()

# Write output with exact target schema column names
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_77/target_multisource_mcts.csv", index=False)