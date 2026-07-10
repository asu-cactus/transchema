import pandas as pd

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_10/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_10/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_10/training_2.csv", index_col=0)

# Join source0 and source1 on user_id
join_01 = pd.merge(source0, source1, on="user_id", how="inner")

# Join the above with source2 on movie_id
join_result = pd.merge(join_01, source2, on="movie_id", how="inner")

# Convert columns to appropriate types before aggregation
join_result["age"] = pd.to_numeric(join_result["age"], errors='coerce').fillna(0).astype(int)
join_result["gender"] = join_result["gender"].map({"M": 1, "F": 2}).fillna(0).astype(int)
join_result["occupation"] = pd.to_numeric(join_result["occupation"], errors='coerce').fillna(0).astype(int)
join_result["zip"] = pd.to_numeric(join_result["zip"], errors='coerce').fillna(0).astype(int)
join_result["user_id"] = pd.to_numeric(join_result["user_id"], errors='coerce').fillna(0).astype(int)
join_result["rating"] = pd.to_numeric(join_result["rating"], errors='coerce').fillna(0).astype(int)
join_result["timestamp"] = pd.to_numeric(join_result["timestamp"], errors='coerce').fillna(0).astype(int)

# Group by movie_id, movie_title (string), year (string)
grouped = join_result.groupby(
    ["movie_id", "movie_title", "year"], as_index=False
).agg({
    "user_id": "max",
    "rating": "max",
    "timestamp": "max",
    "age": "max",
    "gender": "max",
    "occupation": "max",
    "zip": "max"
})

# Rename movie_title and year to movie_title_y and year_y (string columns)
grouped = grouped.rename(columns={"movie_title": "movie_title_y", "year": "year_y"})

# Create movie_title_x as category codes of movie_title_y
grouped["movie_title_x"] = grouped["movie_title_y"].astype('category').cat.codes

# Create year_x as integer conversion of year_y
grouped["year_x"] = pd.to_numeric(grouped["year_y"], errors='coerce').fillna(0).astype(int)

# Reorder columns to match target schema
final_cols = [
    "movie_id", "movie_title_x", "year_x", "user_id", "rating", "timestamp",
    "age", "gender", "occupation", "zip", "movie_title_y", "year_y"
]

result = grouped[final_cols]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_10/target_multisource_mcts.csv", index=False)