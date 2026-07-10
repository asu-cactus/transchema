import pandas as pd

# Read all source tables (assuming there is a second source file named training_1.csv)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_77/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_77/training_1.csv", index_col=0)

# Union all source tables
df_all = pd.concat([df0, df1], ignore_index=True)

# Group by fac_type and sum capacity
result = df_all.groupby("fac_type", as_index=False)["capacity"].sum()

# Ensure capacity is integer type
result["capacity"] = result["capacity"].astype(int)

# Write output with exact target schema column names
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_77/target_multisource_mcts.csv", index=False)