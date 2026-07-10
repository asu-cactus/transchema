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

# Read all sources into a list of dataframes
dfs = [pd.read_csv(f, index_col=0) for f in files]

# Rename columns to avoid collision except 'anime_id' and 'members'
# We only need 'anime_id', 'genre', and 'members' from each source.
# We'll keep 'members' from the first source only to avoid double counting.
# But since members is the same for the same anime_id across sources, we can keep from any one source.

# Extract anime_id and members from the first source
df_base = dfs[0][['anime_id', 'members']].copy()

# For each other source, keep anime_id and genre, rename genre to genre_i
for i, df in enumerate(dfs):
    dfs[i] = df[['anime_id', 'genre']].copy()
    dfs[i].rename(columns={'genre': f'genre_{i}'}, inplace=True)

# Merge all genre columns on anime_id
from functools import reduce

df_merged = reduce(lambda left, right: pd.merge(left, right, on='anime_id', how='outer'), dfs)

# Add members column from df_base (members per anime_id)
df_merged = pd.merge(df_merged, df_base, on='anime_id', how='left')

# Now unpivot all genre columns to get all genres per anime_id
genre_cols = [col for col in df_merged.columns if col.startswith('genre_')]

df_unpivot = df_merged.melt(id_vars=['anime_id', 'members'], value_vars=genre_cols, value_name='genre')

# Drop rows with null genre
df_unpivot = df_unpivot.dropna(subset=['genre'])

# Group by genre and sum members
df_result = df_unpivot.groupby('genre', as_index=False)['members'].sum()

# Convert members to int
df_result['members'] = df_result['members'].astype(int)

# Write to CSV
df_result.to_csv("autopipeline-benchmarks/github-pipelines/length9_76/target_multisource_mcts.csv", index=False)