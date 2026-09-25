import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_25/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_25/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_25/training_2.csv", index_col=0)

# Join ratings with movies on movie_id to get title
merged_1_2 = pd.merge(df1, df2, on='movie_id', how='inner')

# Join the above with user info on user_id
merged_all = pd.merge(merged_1_2, df0, on='user_id', how='inner')

# Group by title, user_id, movie_id and aggregate other columns by mean
result = merged_all.groupby(['title', 'user_id', 'movie_id'], as_index=False).agg({
    'rating': 'mean',
    'timestamp': 'mean',
    'age': 'mean',
    'occupation': 'mean'
})

# Reorder columns to match target schema exactly
result = result[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_25/target_multisource_mcts.csv", index=False)