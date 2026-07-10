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
    # Clean Year column: extract the year as integer from strings like "2010 (83rd)"
    df['Year'] = df['Year'].str.extract(r'(\d{4})').astype(int)
    # Normalize Winner column: convert 'YES' to 1, else 0
    df['Winner'] = df['Winner'].str.upper().eq('YES').astype(int)
    # Convert Nominee and Movie columns to counts (number of nominees/movies per group)
    # But target schema expects integer counts for Nominee and Movie columns.
    # However, Nominee and Movie columns are strings, so we will count distinct Nominee and Movie per group.
    dfs.append(df)

# Concatenate all source tables
all_data = pd.concat(dfs, ignore_index=True)

# Group by Category, Year, Nominee, Movie, Winner and count occurrences as Nominee and Movie counts
# But target schema expects Nominee and Movie as integer counts per Category and Year.
# The target examples show Nominee, Movie, Winner columns as integers equal to counts per Category and Year.
# So we need to group by Category and Year, and count distinct Nominee and Movie, and count Winner=1 occurrences.

grouped = all_data.groupby(['Category', 'Year'], as_index=False).agg(
    Nominee=('Nominee', 'nunique'),
    Movie=('Movie', 'nunique'),
    Winner=('Winner', 'sum')
)

grouped['Nominee'] = grouped['Nominee'].astype(int)
grouped['Movie'] = grouped['Movie'].astype(int)
grouped['Winner'] = grouped['Winner'].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_93/target_multisource_mcts.csv", index=False)