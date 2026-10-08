import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_93/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_93/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_93/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_93/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_93/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Extract year as integer
df['Year'] = df['Year'].str.extract(r'(\d{4})').astype(int)

# Map Winner to 1/0
df['Winner'] = df['Winner'].map({'YES': 1, 'NO': 0}).fillna(0).astype(int)

# Group by Category and aggregate counts of distinct values
result = df.groupby('Category').agg(
    Year=('Year', 'nunique'),
    Nominee=('Nominee', 'nunique'),
    Movie=('Movie', 'nunique'),
    Winner=('Winner', 'nunique')
).reset_index()

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_93/target_multisource_mcts.csv", index=False)