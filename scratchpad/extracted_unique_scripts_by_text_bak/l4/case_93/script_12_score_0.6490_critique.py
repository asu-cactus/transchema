import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_2.csv", index_col=0)

# Join s2 (ratings) with s0 (users) on user_id
joined_0_2 = pd.merge(s2, s0, on="user_id", how="inner")

# Join the above with s1 (movies) on movie_id
final_join = pd.merge(joined_0_2, s1, on="movie_id", how="inner")

# Create title_x and genres_x as counts of ratings per movie_id (integer)
counts = s2.groupby("movie_id").size().reset_index(name="count")
counts = counts.rename(columns={"count": "title_x"})
final = pd.merge(final_join, counts, on="movie_id", how="left")
final["genres_x"] = final["title_x"]

# Map gender to integer: M=1, F=2, else 0
final["gender"] = final["gender"].map({"M":1, "F":2}).fillna(0).astype(int)

# Extract numeric part of zip and convert to int
final["zip"] = final["zip"].astype(str).str.extract(r'(\d+)').fillna('0').astype(int)

# Convert age and occupation to int, coercing errors to 0
final["age"] = pd.to_numeric(final["age"], errors='coerce').fillna(0).astype(int)
final["occupation"] = pd.to_numeric(final["occupation"], errors='coerce').fillna(0).astype(int)

# Convert rating and timestamp to int
final["rating"] = final["rating"].astype(int)
final["timestamp"] = final["timestamp"].astype(int)

# Convert movie_id and user_id to int
final["movie_id"] = final["movie_id"].astype(int)
final["user_id"] = final["user_id"].astype(int)

# Convert title_x and genres_x to int
final["title_x"] = final["title_x"].astype(int)
final["genres_x"] = final["genres_x"].astype(int)

# title_y and genres_y are strings from s1
final["title_y"] = final["title"].astype(str)
final["genres_y"] = final["genres"].astype(str)

# Select and reorder columns to match target schema exactly
final = final[[
    "movie_id", "user_id", "rating", "timestamp", "gender", "age", "occupation", "zip",
    "title_x", "genres_x", "title_y", "genres_y"
]]

# Write output
final.to_csv("autopipeline-benchmarks/github-pipelines/length4_93/target_multisource_mcts.csv", index=False)