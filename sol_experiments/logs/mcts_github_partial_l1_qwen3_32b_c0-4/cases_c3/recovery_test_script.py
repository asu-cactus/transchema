import pandas as pd

# Load source data
source_path = "autopipeline-benchmarks/github-pipelines/length1_3/test_0.csv"
source_df = pd.read_csv(source_path, index_col=0)

# Group by Major_category and compute aggregate Median
result_df = source_df.groupby("Major_category")["Median"].mean().reset_index()

# Save to target file
result_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_3/target_multisource_mcts_recovery_test_val.csv", index=False)