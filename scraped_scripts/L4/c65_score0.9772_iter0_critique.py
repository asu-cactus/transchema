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

# Group by the key columns to remove duplicates, aggregating other columns by first value
df = df.groupby(['Year', 'Category', 'Nominee'], as_index=False).agg({
    'Movie': 'first',
    'Winner': 'first'
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_65/target_multisource_mcts.csv", index=False)