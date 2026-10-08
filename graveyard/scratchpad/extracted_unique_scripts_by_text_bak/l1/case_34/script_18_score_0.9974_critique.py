import pandas as pd

# List all source file paths
source_files = [
    "autopipeline-benchmarks/github-pipelines/length1_34/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_34/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_34/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_34/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_34/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_34/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length1_34/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length1_34/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length1_34/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length1_34/training_9.csv",
]

# Read all source tables and rename column
dfs = [pd.read_csv(f, index_col=0).rename(columns={"J_CALL": "V_GENE"}) for f in source_files]

# Union all dataframes (concatenate)
result = pd.concat(dfs, ignore_index=True)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_34/target_multisource_mcts.csv", index=False)