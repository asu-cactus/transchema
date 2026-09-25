import pandas as pd

# Read all source tables (only one source table given here, but if more exist, read them similarly)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_11/training_0.csv", index_col=0)

# If multiple source tables existed, they would be unioned here, e.g.:
# df1 = pd.read_csv("path_to_source1.csv", index_col=0)
# df_all = pd.concat([df0, df1], ignore_index=True)
# Since only one source is given, just use df0 as df_all
df_all = df0

# Group by 'sex' and sum 'births'
result = df_all.groupby("sex", as_index=False)["births"].sum()

# Ensure correct types
result["sex"] = result["sex"].astype(str)
result["births"] = result["births"].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_11/target_multisource_mcts.csv", index=False)