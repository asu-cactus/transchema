import pandas as pd

# Read the single source table (only one source given)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_54/training_0.csv", index_col=0)

# Since only one source is given, UNION is trivial (just use df0)
df_union = df0

# Group by 'condition' and sum 'click'
result = df_union.groupby("condition", as_index=False)["click"].sum()

# Ensure correct types
result["condition"] = result["condition"].astype(int)
result["click"] = result["click"].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_54/target_multisource_mcts.csv", index=False)