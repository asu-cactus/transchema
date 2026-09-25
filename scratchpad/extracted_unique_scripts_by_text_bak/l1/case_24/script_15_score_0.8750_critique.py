import pandas as pd

# Read all source tables (only one source given here)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_24/training_0.csv", index_col=0)

# Since only one source is given, union is trivial (just df0)
df_union = df0

# Group by 'condition' and sum 'click'
result = df_union.groupby("condition", as_index=False)["click"].sum()

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_24/target_multisource_mcts.csv", index=False)