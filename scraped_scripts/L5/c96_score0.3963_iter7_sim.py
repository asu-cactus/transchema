import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_96/training_0.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_96/training_2.csv", index_col=0)

merged = pd.merge(source2, source0, on="Cust_id")
result = merged.groupby("Profit", as_index=False).size()
# The above groupby on Profit with size() produces counts per Profit, but target schema only has Profit column.
# The partial plan says GROUP_BY : [Profit], but target schema is only Profit (float).
# Grouping by Profit alone and aggregating counts would produce counts, not Profit values.
# The target examples show Profit values, so likely the intention is to aggregate Profit values, e.g., sum or mean.
# Since Profit is float and target schema is only Profit, we should aggregate Profit by sum or mean.
# The partial plan is ambiguous, but likely the goal is to sum Profit grouped by Cust_id or something else.
# However, the partial plan only says GROUP_BY : [Profit], which is unusual.
# Reconsider: The partial plan is JOIN on Cust_id, then GROUP_BY Profit.
# Grouping by Profit itself is strange because Profit is float and target schema is only Profit.
# Possibly the target is the sum of Profit over all rows (no grouping key).
# The target examples have 3 rows with different Profit values, so maybe grouping by Profit is just a hint to aggregate Profit values.
# Since no other grouping key is given, and target schema is only Profit, the best guess is to aggregate Profit by sum or mean over the entire joined table.
# But target examples have multiple rows, so maybe the grouping is by Cust_id or some other key.
# Since the partial plan is incomplete, let's reason:
# Source2 has Profit and Cust_id.
# Source0 has Cust_id and customer info.
# Joining on Cust_id gives Profit per customer.
# Target schema is only Profit.
# The target examples have 3 rows with different Profit values.
# So maybe the target is the sum of Profit per Cust_id.
# So group by Cust_id and sum Profit.
# Then output only the Profit column.
# This matches the target schema and examples.

# Implementing that:

result = merged.groupby("Cust_id", as_index=False)["Profit"].sum()
result = result[["Profit"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_96/target_multisource_mcts.csv", index=False)