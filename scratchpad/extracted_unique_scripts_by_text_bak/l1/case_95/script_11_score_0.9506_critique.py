import pandas as pd

# Read all source tables (only one given here)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_95/training_0.csv", index_col=0)

# UNION all source tables (only one here)
df_union = pd.concat([df0], ignore_index=True)

# GROUP BY customer_id, aggregate min date
df_grouped = df_union.groupby("customer_id", as_index=False).agg({"date": "min"})

# Ensure types match target schema
df_grouped["customer_id"] = df_grouped["customer_id"].astype(int)
df_grouped["date"] = df_grouped["date"].astype(str)

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_95/target_multisource_mcts.csv", index=False)