import pandas as pd

# Read source tables with index_col=0 as instructed
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_2.csv", index_col=0)

# Join source1 and source2 on user_id (inner join)
join_1_2 = source1.merge(source2, on="user_id", how="inner")

# Join the above with source0 on movie_id (inner join)
full_join = join_1_2.merge(source0[['movie_id', 'title', 'video_release_date']], on="movie_id", how="inner")

# Prepare final dataframe with target schema columns
result = pd.DataFrame()
result['title'] = full_join['title']
result['movie_id'] = full_join['movie_id'].astype('Int64')  # integer type with nullable support
result['video_release_date'] = pd.to_numeric(full_join['video_release_date'], errors='coerce')
result['user_id'] = full_join['user_id'].astype(float)
result['rating'] = full_join['rating'].astype(float)
result['unix_timestamp'] = full_join['unix_timestamp'].astype(float)
result['age'] = full_join['age'].astype(float)

# Write to output CSV without index
result.to_csv("autopipeline-benchmarks/github-pipelines/length3_91/target_multisource_mcts.csv", index=False)