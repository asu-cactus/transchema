import pandas as pd

# List all source files
source_files = [
    "autopipeline-benchmarks/github-pipelines/length1_80/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_80/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_80/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_80/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_80/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_80/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length1_80/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length1_80/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length1_80/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length1_80/training_9.csv",
]

# Read and concatenate all source tables
dfs = []
for file in source_files:
    df = pd.read_csv(file, index_col=0)
    df = df[['movieId', 'rating']]
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)

# Ensure correct types
df_all['movieId'] = df_all['movieId'].astype(int)
df_all['rating'] = df_all['rating'].astype(float)

# Group by movieId and compute mean rating
df_result = df_all.groupby('movieId', as_index=False)['rating'].mean()

# Write output
df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_80/target_multisource_mcts.csv", index=False)