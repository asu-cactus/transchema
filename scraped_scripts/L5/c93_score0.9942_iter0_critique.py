import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_93/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_93/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_93/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_93/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_93/training_4.csv",
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    # Extract year as integer from strings like "2010 (83rd)"
    df['Year'] = df['Year'].str.extract(r'(\d{4})').astype(int)
    # Normalize Winner column: convert 'YES' to 1, else 0
    df['Winner'] = df['Winner'].str.upper().eq('YES').astype(int)
    dfs.append(df)

# UNION all source tables by concatenation
all_data = pd.concat(dfs, ignore_index=True)

# GROUP BY Category only, aggregate counts of distinct Year, Nominee, Movie, and sum of Winner
grouped = all_data.groupby('Category', as_index=False).agg(
    Year=('Year', 'nunique'),
    Nominee=('Nominee', 'nunique'),
    Movie=('Movie', 'nunique'),
    Winner=('Winner', 'sum')
)

# Ensure integer types for aggregated columns
grouped['Year'] = grouped['Year'].astype(int)
grouped['Nominee'] = grouped['Nominee'].astype(int)
grouped['Movie'] = grouped['Movie'].astype(int)
grouped['Winner'] = grouped['Winner'].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_93/target_multisource_mcts.csv", index=False)