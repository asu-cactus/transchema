import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_27/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_27/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_27/training_2.csv", index_col=0)

# Join df0 and df1 on user_id (inner join to keep only matching users)
joined_01 = pd.merge(df0, df1[['user_id', 'age', 'occupation']], on='user_id', how='inner')

# Join the above with df2 on movie_id (inner join to keep only matching movies)
joined_all = pd.merge(joined_01, df2[['movie_id', 'title']], on='movie_id', how='inner')

# Group by title, user_id, movie_id and aggregate numeric columns by mean
final = joined_all.groupby(['title', 'user_id', 'movie_id'], as_index=False).agg({
    'rating': 'mean',
    'timestamp': 'mean',
    'age': 'mean',
    'occupation': 'mean'
})

# Reorder columns to match target schema exactly
final = final[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_27/target_multisource_mcts.csv", index=False)