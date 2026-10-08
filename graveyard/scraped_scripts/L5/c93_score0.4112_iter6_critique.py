import pandas as pd

# Read all source files
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_93/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_93/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_93/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_93/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_93/training_4.csv", index_col=0)

# Concatenate all sources (UNION)
all_sources = pd.concat([s0, s1, s2, s3, s4], ignore_index=True)

# Clean Year column: extract integer year from string like "2010 (83rd)"
def clean_year(y):
    if isinstance(y, str):
        y = y.split(' ')[0]
    try:
        return int(y)
    except:
        return pd.NA

all_sources['Year'] = all_sources['Year'].map(clean_year).astype('Int64')

# Ensure Category is string
all_sources['Category'] = all_sources['Category'].astype(str)

# Clean Winner column: 1 if "YES" (case-insensitive), else 0
def winner_to_int(w):
    if isinstance(w, str) and w.strip().upper() == 'YES':
        return 1
    try:
        return int(w)
    except:
        return 0

all_sources['Winner'] = all_sources['Winner'].map(winner_to_int).astype('Int64')

# Strip whitespace from Nominee and Movie to avoid counting empty strings
all_sources['Nominee'] = all_sources['Nominee'].astype(str).str.strip()
all_sources['Movie'] = all_sources['Movie'].astype(str).str.strip()

# Group by Category and Year, aggregate counts of distinct Nominee, distinct Movie, and sum of Winner
result = (
    all_sources
    .groupby(['Category', 'Year'], dropna=False)
    .agg(
        Nominee=('Nominee', lambda x: x[x != ''].nunique()),
        Movie=('Movie', lambda x: x[x != ''].nunique()),
        Winner=('Winner', 'sum')
    )
    .reset_index()
)

# Convert all aggregated columns to integer type
result['Nominee'] = result['Nominee'].astype('Int64')
result['Movie'] = result['Movie'].astype('Int64')
result['Winner'] = result['Winner'].astype('Int64')

# Write output with exact target schema column order
result = result[['Category', 'Year', 'Nominee', 'Movie', 'Winner']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_93/target_multisource_mcts.csv", index=False)