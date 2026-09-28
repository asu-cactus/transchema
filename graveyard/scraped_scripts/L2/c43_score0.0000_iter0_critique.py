import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_43/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_43/training_1.csv", index_col=0)

# Select only relevant columns from each source to avoid duplication and conflicts
cols_to_use_0 = ['artist_name', 'speechiness', 'instrumentalness', 'danceability', 'energy', 'acousticness']
cols_to_use_1 = ['artist_name', 'speechiness', 'instrumentalness', 'danceability', 'energy', 'acousticness']

df0_sel = df0[cols_to_use_0]
df1_sel = df1[cols_to_use_1]

# Rename columns in df1 to distinguish before join
df1_sel_renamed = df1_sel.rename(columns={
    'speechiness': 'speechiness_1',
    'instrumentalness': 'instrumentalness_1',
    'danceability': 'danceability_1',
    'energy': 'energy_1',
    'acousticness': 'acousticness_1'
})

# Join on artist_name (inner join)
df_joined = pd.merge(df0_sel, df1_sel_renamed, on='artist_name', how='inner')

# Compute mean of each pair of columns from both sources
result = pd.DataFrame()
result['artist_name'] = df_joined['artist_name']
result['speechiness'] = (df_joined['speechiness'] + df_joined['speechiness_1']) / 2
result['instrumentalness'] = (df_joined['instrumentalness'] + df_joined['instrumentalness_1']) / 2
result['danceability'] = (df_joined['danceability'] + df_joined['danceability_1']) / 2
result['energy'] = (df_joined['energy'] + df_joined['energy_1']) / 2
result['acousticness'] = (df_joined['acousticness'] + df_joined['acousticness_1']) / 2

# Group by artist_name to aggregate multiple rows per artist (if any)
result = result.groupby('artist_name', as_index=False).mean()

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_43/target_multisource_mcts.csv", index=False)