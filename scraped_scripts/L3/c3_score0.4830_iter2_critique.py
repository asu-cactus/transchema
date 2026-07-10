import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_3/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_3/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_3/training_2.csv", index_col=0)

# Join ratings with movies on movie_id
join_1 = pd.merge(source2, source1, on="movie_id", how="inner")

# Join the above with users on user_id
join_result = pd.merge(join_1, source0, on="user_id", how="inner")

# Group by title, user_id, movie_id and aggregate other columns by mean
grouped = join_result.groupby(["title", "user_id", "movie_id"], as_index=False).agg({
    "age": "mean",
    "occupation": "mean",
    "rating": "mean",
    "timestamp": "mean"
})

# Ensure correct dtypes and column order as per target schema
grouped = grouped.astype({
    "title": str,
    "user_id": float,
    "age": float,
    "occupation": float,
    "movie_id": int,
    "rating": float,
    "timestamp": float
})

# Reorder columns to match target schema exactly
grouped = grouped[["title", "user_id", "age", "occupation", "movie_id", "rating", "timestamp"]]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_3/target_multisource_mcts.csv", index=False)