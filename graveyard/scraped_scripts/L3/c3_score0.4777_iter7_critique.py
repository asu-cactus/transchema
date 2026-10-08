import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length3_3/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length3_3/training_1.csv', index_col=0)
df2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length3_3/training_2.csv', index_col=0)

# Join ratings with user info on user_id
joined_0 = pd.merge(df2, df0[['user_id', 'age', 'occupation']], on='user_id', how='inner')

# Join the above with movie info on movie_id
joined_1 = pd.merge(joined_0, df1[['movie_id', 'title']], on='movie_id', how='inner')

# Group by title, user_id, movie_id and aggregate other columns by mean
agg = joined_1.groupby(['title', 'user_id', 'movie_id'], as_index=False).agg({
    'age': 'mean',
    'occupation': 'mean',
    'rating': 'mean',
    'timestamp': 'mean'
})

# Reorder columns to match target schema
agg = agg[['title', 'user_id', 'age', 'occupation', 'movie_id', 'rating', 'timestamp']]

agg.to_csv('autopipeline-benchmarks/github-pipelines/length3_3/target_multisource_mcts.csv', index=False)