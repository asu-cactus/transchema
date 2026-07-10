import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_33/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_33/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_33/training_2.csv", index_col=0)

# Join ratings with movies on movie_id
join_0 = pd.merge(source2, source0, on="movie_id", how="inner")

# Join the above with users on user_id
join_1 = pd.merge(join_0, source1, on="user_id", how="inner")

# Group by title and aggregate by mean for numeric columns
result = join_1.groupby("title", as_index=False).agg({
    "user_id": "mean",
    "movie_id": "mean",
    "rating": "mean",
    "timestamp": "mean",
    "age": "mean",
    "occupation": "mean"
})

# Cast columns to match target schema types
result["user_id"] = result["user_id"].astype(float)
result["movie_id"] = result["movie_id"].astype(int)
result["rating"] = result["rating"].astype(float)
result["timestamp"] = result["timestamp"].astype(float)
result["age"] = result["age"].astype(float)
result["occupation"] = result["occupation"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_33/target_multisource_mcts.csv", index=False)