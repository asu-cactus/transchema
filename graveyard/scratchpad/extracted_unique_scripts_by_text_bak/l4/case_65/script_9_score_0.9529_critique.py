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

df = df.astype({
    'Year': str,
    'Category': str,
    'Nominee': str,
    'Movie': str,
    'Winner': str
})

# Remove duplicates by grouping on all columns (equivalent to drop_duplicates)
df = df.drop_duplicates(subset=['Year', 'Category', 'Nominee', 'Movie', 'Winner'])

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_65/target_multisource_mcts.csv", index=False)