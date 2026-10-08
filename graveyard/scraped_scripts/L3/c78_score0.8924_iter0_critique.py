import pandas as pd

df_ratings = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_78/training_0.csv", index_col=0)
df_users = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_78/training_1.csv", index_col=0)
df_movies = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_78/training_2.csv", index_col=0)

# Join ratings with users on user_id to get sex
df = df_ratings.merge(df_users[['user_id', 'sex']], on='user_id', how='inner')

# Group by movie_id and sex, aggregate mean rating
agg = df.groupby(['movie_id', 'sex'], as_index=False)['rating'].mean()

# Pivot sex to columns F and M
agg_pivot = agg.pivot(index='movie_id', columns='sex', values='rating')

# Rename columns to F and M exactly
agg_pivot = agg_pivot.rename(columns={'F': 'F', 'M': 'M'})

# Reset index to have movie_id as column
agg_pivot = agg_pivot.reset_index()

# Join movies with aggregated ratings on movie_id using inner join to keep only movies with ratings
df_result = df_movies[['movie_id', 'title']].merge(agg_pivot, on='movie_id', how='inner')

# Ensure columns order as target schema
df_result = df_result[['movie_id', 'title', 'F', 'M']]

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length3_78/target_multisource_mcts.csv", index=False)