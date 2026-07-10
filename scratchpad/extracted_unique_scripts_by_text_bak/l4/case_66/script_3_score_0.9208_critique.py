import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_66/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_66/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_66/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_66/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length4_66/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Remove duplicate rows to match target unique rows
df = df.drop_duplicates(subset=['Year', 'Category', 'Nominee', 'Movie', 'Winner'])

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_66/target_multisource_mcts.csv", index=False)