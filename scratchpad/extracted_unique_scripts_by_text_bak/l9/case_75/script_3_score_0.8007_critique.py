import pandas as pd

# List of all source CSV file paths
source_files = [
    "autopipeline-benchmarks/github-pipelines/length9_75/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_14.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_15.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_16.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_17.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_18.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_19.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_20.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_21.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_22.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_23.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_24.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_25.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_26.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_27.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_28.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_29.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_30.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_31.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_32.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_33.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_34.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_35.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_36.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_37.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_38.csv",
]

# Read all source tables into a list of DataFrames
dfs = [pd.read_csv(f, index_col=0) for f in source_files]

# Concatenate all DataFrames (UNION)
result = pd.concat(dfs, ignore_index=True)

# Ensure columns are in the exact order as target schema
target_columns = ['anime_id', 'name', 'genre', 'type', 'episodes', 'rating', 'members']
result = result[target_columns]

# Write the final output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_75/target_multisource_mcts.csv", index=False)