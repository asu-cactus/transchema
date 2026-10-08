import pandas as pd

# Load all source tables with index_col=0 to skip the first column
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_66/test_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_66/test_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_66/test_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_66/test_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_66/test_4.csv", index_col=0)

# Perform union of all source tables
combined_df = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

# Save to target file
combined_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_66/target_multisource_mcts_recovery_test_val.csv", index=False)