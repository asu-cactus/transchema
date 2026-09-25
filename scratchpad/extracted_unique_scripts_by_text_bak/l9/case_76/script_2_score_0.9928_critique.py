import pandas as pd

files = [
    "autopipeline-benchmarks/github-pipelines/length9_76/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_14.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_15.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_16.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_17.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_18.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_19.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_20.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_21.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_22.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_23.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_24.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_25.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_26.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_27.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_28.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_29.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_30.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_31.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_32.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_33.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_34.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_35.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_36.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_37.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_38.csv",
]

# Read all source tables
dfs = [pd.read_csv(f, index_col=0) for f in files]

# Rename columns to avoid collision except 'anime_id'
# We'll suffix genre columns with source index to distinguish
for i, df in enumerate(dfs):
    df.columns = ['anime_id', f'name_{i}', f'genre_{i}', f'type_{i}', f'episodes_{i}', f'rating_{i}', f'members_{i}']

# Start with the first dataframe
df_merged = dfs[0]

# Iteratively join all other dfs on 'anime_id' using outer join to keep all animes
for df in dfs[1:]:
    df_merged = df_merged.merge(df, on='anime_id', how='outer')

# Extract all genre columns and members columns
genre_cols = [col for col in df_merged.columns if col.startswith('genre_')]
members_cols = [col for col in df_merged.columns if col.startswith('members_')]

# For members, since they should be the same per anime, take the first non-null value per row
df_merged['members'] = df_merged[members_cols].bfill(axis=1).iloc[:, 0]

# Melt genres into one column per anime
df_genres = df_merged[['anime_id'] + genre_cols].melt(id_vars=['anime_id'], value_vars=genre_cols, value_name='genre')

# Drop rows with null genre
df_genres = df_genres.dropna(subset=['genre'])

# Drop duplicates of (anime_id, genre)
df_genres = df_genres.drop_duplicates(subset=['anime_id', 'genre'])

# Join back members to genres on anime_id
df_genres = df_genres.merge(df_merged[['anime_id', 'members']], on='anime_id', how='left')

# Group by genre and sum members
df_result = df_genres.groupby('genre', as_index=False)['members'].sum()

# Ensure correct types
df_result['genre'] = df_result['genre'].astype(str)
df_result['members'] = df_result['members'].astype(int)

# Write output
df_result.to_csv("autopipeline-benchmarks/github-pipelines/length9_76/target_multisource_mcts.csv", index=False)