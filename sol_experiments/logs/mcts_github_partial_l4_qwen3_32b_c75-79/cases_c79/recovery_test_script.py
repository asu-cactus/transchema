import pandas as pd

# Load all source files
source_paths = [
    "autopipeline-benchmarks/github-pipelines/length4_79/test_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_79/test_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_79/test_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_79/test_3.csv",
    "autopipeline-benchmarks/github-pipelines/length4_79/test_4.csv"
]

dfs = [pd.read_csv(path, index_col=0) for path in source_paths]

# Combine sources via union
combined_df = pd.concat(dfs, ignore_index=True)

# Save to target location
target_path = "autopipeline-benchmarks/github-pipelines/length4_79/target_multisource_mcts_recovery_test_val.csv"
combined_df.to_csv(target_path, index=False)