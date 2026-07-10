import pandas as pd

# Read all source tables with the same schema
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_23/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_23/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_23/training_2.csv", index_col=0)

# Union all source tables
df_all = pd.concat([df0, df1, df2], ignore_index=True)

# Group by customer_id and aggregate average amount
result = df_all.groupby("customer_id", as_index=False)["amount"].mean()

# Ensure correct types
result["customer_id"] = result["customer_id"].astype(int)
result["amount"] = result["amount"].astype(float)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_23/target_multisource_mcts.csv", index=False)