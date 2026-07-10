import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_59/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_59/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_59/training_2.csv", index_col=0)

# Join ratings with users on user_id
join_1 = pd.merge(source2, source1, on="user_id", how="inner")

# Join the above with movies on movie_id
join_2 = pd.merge(join_1, source0, on="movie_id", how="inner")

# Group by user_id, movie_id, timestamp to ensure uniqueness
# For aggregation, take the first value of each column (other than group by columns)
agg_dict = {
    "rating": "first",
    "gender": "first",
    "age": "first",
    "occupation": "first",
    "zip": "first",
    "title": "first",
    "genres": "first"
}

grouped = join_2.groupby(["user_id", "movie_id", "timestamp"], as_index=False).agg(agg_dict)

# Reorder columns to match target schema
target = grouped[[
    "user_id", "movie_id", "rating", "timestamp",
    "gender", "age", "occupation", "zip",
    "title", "genres"
]]

target.to_csv("autopipeline-benchmarks/github-pipelines/length2_59/target_multisource_mcts.csv", index=False)