import pandas as pd

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_0.csv", index_col=0)  # movies
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_1.csv", index_col=0)  # users
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_2.csv", index_col=0)  # ratings

# Join ratings with movies on movie_id
df = df2.merge(df0, on='movie_id', how='inner')

# Join the above with users on user_id
df = df.merge(df1, on='user_id', how='inner')

# Group by title and movie_id, aggregate other columns by mean
agg_df = df.groupby(['title', 'movie_id'], as_index=False).agg({
    'user_id': 'mean',
    'rating': 'mean',
    'unix_timestamp': 'mean',
    'age': 'mean',
    'video_release_date': 'mean'
})

# Ensure correct dtypes and column order as target schema
agg_df['movie_id'] = agg_df['movie_id'].astype('Int64')
agg_df['user_id'] = agg_df['user_id'].astype(float)
agg_df['rating'] = agg_df['rating'].astype(float)
agg_df['unix_timestamp'] = agg_df['unix_timestamp'].astype(float)
agg_df['age'] = agg_df['age'].astype(float)
agg_df['video_release_date'] = pd.to_numeric(agg_df['video_release_date'], errors='coerce')

# Reorder columns exactly as target schema
result = agg_df[['title', 'movie_id', 'video_release_date', 'user_id', 'rating', 'unix_timestamp', 'age']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length3_92/target_multisource_mcts.csv", index=False)