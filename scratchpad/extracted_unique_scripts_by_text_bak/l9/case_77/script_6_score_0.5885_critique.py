import pandas as pd
from functools import reduce

sources = [
    "autopipeline-benchmarks/github-pipelines/length9_77/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_14.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_15.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_16.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_17.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_18.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_19.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_20.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_21.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_22.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_23.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_24.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_25.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_26.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_27.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_28.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_29.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_30.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_31.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_32.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_33.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_34.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_35.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_36.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_37.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_38.csv",
]

# Read all sources
dfs = [pd.read_csv(path, index_col=0) for path in sources]

# Standardize types
for df in dfs:
    df['anime_id'] = pd.to_numeric(df['anime_id'], errors='coerce').astype('Int64')
    df['name'] = df['name'].astype(str)
    df['genre'] = df['genre'].astype(str)
    df['type'] = df['type'].astype(str)
    df['episodes'] = pd.to_numeric(df['episodes'], errors='coerce').astype('Int64')
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce').astype(float)
    df['members'] = pd.to_numeric(df['members'], errors='coerce').astype('Int64')

# Merge all dataframes on 'anime_id' using outer join to keep all anime_ids
# We will keep columns from all dfs with suffixes to distinguish genres
# But since all dfs have same schema, we will rename genre columns to unique names before merge

# Rename genre columns to unique names to keep all genre info
for i, df in enumerate(dfs):
    df.rename(columns={'genre': f'genre_{i}'}, inplace=True)

# Merge all dfs on 'anime_id' using reduce and outer join
merged_df = reduce(lambda left, right: pd.merge(left, right, on=['anime_id', 'name', 'type', 'episodes', 'rating', 'members'], how='outer'), dfs)

# After merge, genre columns are genre_0, genre_1, ..., genre_38
genre_cols = [col for col in merged_df.columns if col.startswith('genre_')]

# For each row, combine unique genres from all genre columns into one string separated by comma
def combine_genres(row):
    genres = set()
    for col in genre_cols:
        val = row[col]
        if pd.notna(val) and val != 'nan' and val.strip() != '':
            genres.add(val.strip())
    return ', '.join(sorted(genres))

merged_df['genre'] = merged_df.apply(combine_genres, axis=1)

# Select final columns in target schema order
final_df = merged_df[['anime_id', 'name', 'genre', 'type', 'episodes', 'rating', 'members']]

# Ensure correct types
final_df['anime_id'] = final_df['anime_id'].astype(int)
final_df['name'] = final_df['name'].astype(str)
final_df['genre'] = final_df['genre'].astype(str)
final_df['type'] = final_df['type'].astype(str)
final_df['episodes'] = final_df['episodes'].astype(int)
final_df['rating'] = final_df['rating'].astype(float)
final_df['members'] = final_df['members'].astype(int)

# Write to CSV
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_77/target_multisource_mcts.csv", index=False)