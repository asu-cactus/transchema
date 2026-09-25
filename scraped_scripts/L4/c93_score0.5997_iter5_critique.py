import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_2.csv", index_col=0)

# Join ratings with movies on movie_id
join_1 = pd.merge(source2, source1, on="movie_id", how="inner")

# Join the above with users on user_id
final = pd.merge(join_1, source0, on="user_id", how="inner")

# Convert gender to integer: map 'M'->1, 'F'->2, else NaN
final['gender'] = final['gender'].map({'M': 1, 'F': 2}).astype('Int64')

# Clean zip: extract digits and convert to integer, else NaN
final['zip'] = final['zip'].astype(str).str.extract('(\d+)').astype('Int64')

# Rename columns to match target schema exactly
# The target schema is:
# ['movie_id', 'user_id', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip', 'title_x', 'genres_x', 'title_y', 'genres_y']
# From sources:
# - title and genres come from source1 (movies)
# - We have only one title and genres column, so assign them to title_y and genres_y (string)
# - title_x and genres_x are integers in target, but source tables do not have these columns.
#   Since no source columns correspond to title_x and genres_x, fill them with 0 as integer columns.

final['title_x'] = 0
final['genres_x'] = 0

# Select and reorder columns exactly as target schema
final = final[['movie_id', 'user_id', 'rating', 'timestamp', 'gender', 'age', 'occupation', 'zip',
               'title_x', 'genres_x', 'title', 'genres']]

# Rename 'title' and 'genres' to 'title_y' and 'genres_y'
final = final.rename(columns={'title': 'title_y', 'genres': 'genres_y'})

# Ensure correct dtypes
final = final.astype({
    'movie_id': 'int64',
    'user_id': 'int64',
    'rating': 'int64',
    'timestamp': 'int64',
    'gender': 'Int64',
    'age': 'int64',
    'occupation': 'int64',
    'zip': 'Int64',
    'title_x': 'int64',
    'genres_x': 'int64',
    'title_y': 'object',
    'genres_y': 'object'
})

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_93/target_multisource_mcts.csv", index=False)