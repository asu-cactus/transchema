import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_29/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_29/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, left_on="movie id", right_on="movie_id", how="inner")

# Group by 'movie title' and 'movie id', aggregate user_id, movie_id, rating by taking first value
grouped = merged.groupby(['movie title', 'movie id'], as_index=False).agg({
    'user_id': 'first',
    'movie_id': 'first',
    'rating': 'first'
})

# Reorder columns to match target schema
grouped = grouped[['movie title', 'movie id', 'user_id', 'movie_id', 'rating']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_29/target_multisource_mcts.csv", index=False)