import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_65/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_65/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_65/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_65/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length4_65/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Convert all columns to string to match target schema types
df = df.astype(str)

# Remove duplicate rows by grouping on all columns (deduplication)
df = df.drop_duplicates(subset=['Year', 'Category', 'Nominee', 'Movie', 'Winner'])

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_65/target_multisource_mcts.csv", index=False)