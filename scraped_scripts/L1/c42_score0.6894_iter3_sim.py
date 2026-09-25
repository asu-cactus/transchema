import pandas as pd

df_ratings = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_42/training_0.csv", index_col=0)
df_movies = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_42/training_1.csv", index_col=0)

df_pivot = df_ratings.melt(id_vars=['user_id'], value_vars=['item_id', 'rating', 'timestamp'], var_name='variable', value_name='value')
# The above melt is incorrect because item_id, rating, timestamp are columns, but we want to keep them as columns, not pivot them.

# Reconsider: The partial plan says PIVOT and GROUP_BY [user_id].
# But the source ratings table already has user_id, item_id, rating, timestamp columns.
# The target schema is user_id, item_id, rating, timestamp, movie title.
# The movie title is only in the movies table keyed by item_id.
# So the first step is to load ratings as is (no pivot needed).
# The partial plan says PIVOT and GROUP_BY user_id, but that seems unnecessary here.
# Possibly the partial plan is a hint, but the actual operation is just join ratings with movies on item_id.

# So let's just join ratings and movies on item_id.

df_merged = pd.merge(df_ratings, df_movies[['item_id', 'movie title']], on='item_id', how='left')

df_merged = df_merged[['user_id', 'item_id', 'rating', 'timestamp', 'movie title']]

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_42/target_multisource_mcts.csv", index=False)