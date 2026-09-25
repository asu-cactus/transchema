import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_14/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_14/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_14/training_2.csv", index_col=0)

# Join Source1 and Source2 on user_id
join_1_2 = pd.merge(source1, source2, on="user_id", how="inner")

# Join Source0 and the above join on movie_id
final_join = pd.merge(source0, join_1_2, on="movie_id", how="inner")

# Group by title, user_id, movie_id and aggregate by mean for rating, timestamp, age, occupation
agg_df = final_join.groupby(['title', 'user_id', 'movie_id'], as_index=False).agg({
    'rating': 'mean',
    'timestamp': 'mean',
    'age': 'mean',
    'occupation': 'mean'
})

# Reorder columns to match target schema
final = agg_df[['title', 'user_id', 'movie_id', 'rating', 'timestamp', 'age', 'occupation']]

# Cast columns to target types
final['user_id'] = final['user_id'].astype(float)
final['movie_id'] = final['movie_id'].astype(int)
final['rating'] = final['rating'].astype(float)
final['timestamp'] = final['timestamp'].astype(float)
final['age'] = final['age'].astype(float)
final['occupation'] = final['occupation'].astype(float)

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_14/target_multisource_mcts.csv", index=False)