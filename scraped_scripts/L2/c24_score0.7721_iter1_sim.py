import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_24/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_24/training_1.csv"
output_path = "autopipeline-benchmarks/github-pipelines/length2_24/target_multisource_mcts.csv"

df_ratings = pd.read_csv(source0_path, index_col=0)
df_movies = pd.read_csv(source1_path, index_col=0)

pivot = df_ratings.pivot_table(index='movie_id', columns='rating', values='user_id', aggfunc='count', fill_value=0).reset_index()

pivot['size'] = pivot.loc[:, 1:5].sum(axis=1)
pivot['mean'] = sum(pivot[r] * r for r in range(1, 6)) / pivot['size']
pivot = pivot[['movie_id', 'size', 'mean']]

merged = pd.merge(pivot, df_movies, on='movie_id', how='inner')

result = merged[['title', 'size', 'mean']]

result.to_csv(output_path, index=False)