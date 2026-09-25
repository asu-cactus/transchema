import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_2.csv", index_col=0)

# Join ratings with movies on movie_id
join_1 = pd.merge(s2, s1, on="movie_id", how="inner")

# Join the above with users on user_id
join_2 = pd.merge(join_1, s0, on="user_id", how="inner")

# Map gender to integer
join_2["gender"] = join_2["gender"].map({"M":1, "F":0}).fillna(0).astype(int)

# Convert age, occupation to int safely
join_2["age"] = pd.to_numeric(join_2["age"], errors="coerce").fillna(0).astype(int)
join_2["occupation"] = pd.to_numeric(join_2["occupation"], errors="coerce").fillna(0).astype(int)

# Extract numeric part of zip and convert to int
join_2["zip"] = join_2["zip"].astype(str).str.extract(r'(\d+)').fillna("0").astype(int)

# Encode title and genres as categorical codes for title_x and genres_x (integer columns)
join_2["title_x"] = join_2["title"].astype("category").cat.codes + 1
join_2["genres_x"] = join_2["genres"].astype("category").cat.codes + 1

# title_y and genres_y remain as strings
join_2["title_y"] = join_2["title"]
join_2["genres_y"] = join_2["genres"]

# Define aggregation functions
agg_dict = {
    "rating": "max",
    "timestamp": "max",
    "gender": "first",
    "age": "first",
    "occupation": "first",
    "zip": "first",
    "title_x": "first",
    "genres_x": "first",
    "title_y": "first",
    "genres_y": "first"
}

# Group by movie_id and user_id to get unique rows
result = join_2.groupby(["movie_id", "user_id"], as_index=False).agg(agg_dict)

# Reorder columns to match target schema exactly
final_cols = ["movie_id", "user_id", "rating", "timestamp", "gender", "age", "occupation", "zip",
              "title_x", "genres_x", "title_y", "genres_y"]

result = result[final_cols]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_93/target_multisource_mcts.csv", index=False)