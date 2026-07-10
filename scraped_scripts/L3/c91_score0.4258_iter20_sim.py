import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_2.csv", index_col=0)

union_1 = pd.concat([source1, source1], ignore_index=True)
union_0 = pd.concat([source0, source0], ignore_index=True)

join_1_0 = pd.merge(union_1, union_0, on="movie_id", how="inner")

final_join = pd.merge(join_1_0, source2, on="user_id", how="inner")

result = final_join.rename(columns={
    "release_date": "video_release_date"  # but release_date is not used in target, video_release_date is from source0
})

# The target schema is:
# ['title': string, 'movie_id': integer, 'video_release_date': float, 'user_id': float, 'rating': float, 'unix_timestamp': float, 'age': float]

# video_release_date in source0 is float or NaN, keep as is
# user_id, rating, unix_timestamp from source1 (union_1)
# age from source2
# title, movie_id from source0

# Select and convert columns to target schema and types
out = pd.DataFrame()
out["title"] = final_join["title"].astype(str)
out["movie_id"] = final_join["movie_id"].astype(int)
# video_release_date in source0 is string or NaN, convert to float if possible, else NaN
# From source0 examples video_release_date is NaN, so convert to float (will be NaN)
out["video_release_date"] = pd.to_numeric(final_join["video_release_date"], errors='coerce')
out["user_id"] = final_join["user_id"].astype(float)
out["rating"] = final_join["rating"].astype(float)
out["unix_timestamp"] = final_join["unix_timestamp"].astype(float)
out["age"] = final_join["age"].astype(float)

out.to_csv("autopipeline-benchmarks/github-pipelines/length3_91/target_multisource_mcts.csv", index=False)