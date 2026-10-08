import pandas as pd

# List all source files (assuming 5 sources as example, adjust if more)
source_files = [
    "autopipeline-benchmarks/github-pipelines/length1_92/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_92/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_92/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_92/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_92/training_4.csv",
]

dfs = [pd.read_csv(f, index_col=0).astype({"user_id": str, "email": str, "geo": str}) for f in source_files]

result = pd.concat(dfs, ignore_index=True)

# Remove duplicates if any (user_id is primary key)
result = result.drop_duplicates(subset=["user_id"])

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_92/target_multisource_mcts.csv", index=False)