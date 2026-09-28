import pandas as pd

# File paths
paths_dim = {
    "Source9_22_3": "autopipeline-benchmarks/github-pipelines/length9_22/training_3.csv",
    "Source9_22_4": "autopipeline-benchmarks/github-pipelines/length9_22/training_4.csv",
    "Source9_22_7": "autopipeline-benchmarks/github-pipelines/length9_22/training_7.csv",
    "Source9_22_8": "autopipeline-benchmarks/github-pipelines/length9_22/training_8.csv",
}

paths_aspect = {
    "Source9_22_0": "autopipeline-benchmarks/github-pipelines/length9_22/training_0.csv",
    "Source9_22_1": "autopipeline-benchmarks/github-pipelines/length9_22/training_1.csv",
    "Source9_22_2": "autopipeline-benchmarks/github-pipelines/length9_22/training_2.csv",
    "Source9_22_5": "autopipeline-benchmarks/github-pipelines/length9_22/training_5.csv",
    "Source9_22_6": "autopipeline-benchmarks/github-pipelines/length9_22/training_6.csv",
    "Source9_22_9": "autopipeline-benchmarks/github-pipelines/length9_22/training_9.csv",
}

# Read and union dimension tables
dim_dfs = [pd.read_csv(path, index_col=0) for path in paths_dim.values()]
unioned_dim = pd.concat(dim_dfs, ignore_index=True)

# Read aspect tables into dict
aspect_dfs = {name: pd.read_csv(path, index_col=0) for name, path in paths_aspect.items()}

# Join all aspect tables to unioned_dim on ROW_WID
# Start with unioned_dim
df = unioned_dim

for name, aspect_df in aspect_dfs.items():
    df = df.merge(aspect_df, on='ROW_WID', how='inner')

# Project only INBOUND_CALLS_NUM column as per target schema
result = df[['INBOUND_CALLS_NUM']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_22/target_multisource_mcts.csv", index=False)