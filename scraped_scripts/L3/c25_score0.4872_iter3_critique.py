import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_25/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_25/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_25/training_2.csv", index_col=0)

# Join Source1 and Source2 on movie_id to get movie titles
join_1_2 = pd.merge(source1, source2, on="movie_id", how="inner")

# Join the above with Source0 on user_id to get user demographics
final_join = pd.merge(source0, join_1_2, on="user_id", how="inner")

# Group by title, user_id, movie_id and aggregate numeric columns by mean
grouped = final_join.groupby(["title", "user_id", "movie_id"], as_index=False).agg({
    "rating": "mean",
    "timestamp": "mean",
    "age": "mean",
    "occupation": "mean"
})

# Reorder columns to match target schema
result = grouped[["title", "user_id", "movie_id", "rating", "timestamp", "age", "occupation"]]

# Cast columns to target types
result["user_id"] = result["user_id"].astype(float)
result["movie_id"] = result["movie_id"].astype(int)
result["rating"] = result["rating"].astype(float)
result["timestamp"] = result["timestamp"].astype(float)
result["age"] = result["age"].astype(float)
result["occupation"] = result["occupation"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_25/target_multisource_mcts.csv", index=False)