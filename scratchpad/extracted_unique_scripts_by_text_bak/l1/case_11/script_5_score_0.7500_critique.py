import pandas as pd

# Read the single source table (if multiple, read all and union)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_11/training_0.csv", index_col=0)

# Since only one source table is given, union is trivial
df_union = df0

# Group by 'sex' and sum 'births'
result = df_union.groupby("sex", as_index=False)["births"].sum()

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_11/target_multisource_mcts.csv", index=False)