import pandas as pd

# Read the single source table (only one source given)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_54/training_0.csv", index_col=0)

# If there were multiple source tables, we would union them here by concatenation.
# Since only one source is given, union is trivial.

# Group by 'condition' and sum 'click'
result = df0.groupby("condition", as_index=False)["click"].sum()

# Ensure correct types
result["condition"] = result["condition"].astype(int)
result["click"] = result["click"].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_54/target_multisource_mcts.csv", index=False)