import pandas as pd

# Read the single source file (only one source given)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_87/training_0.csv", index_col=0)

# Since only one source is given, union is trivial (just df0)
df_union = df0.copy()

# Group by 'condition' and compute mean of 'click'
result = df_union.groupby("condition", as_index=False)["click"].mean()

# Ensure types match target schema
result["condition"] = result["condition"].astype(int)
result["click"] = result["click"].astype(float)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_87/target_multisource_mcts.csv", index=False)