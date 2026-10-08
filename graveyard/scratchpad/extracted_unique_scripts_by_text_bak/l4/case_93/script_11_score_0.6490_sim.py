import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_2.csv", index_col=0)

agg = s2.groupby("movie_id").agg(
    user_id=("user_id", "count"),
    rating=("rating", "mean"),
    timestamp_min=("timestamp", "min"),
    timestamp_max=("timestamp", "max"),
).reset_index()

joined_0_2 = pd.merge(s2, s0, on="user_id", how="inner")

final_join = pd.merge(joined_0_2, s1, on="movie_id", how="inner")

final = final_join.rename(columns={
    "movie_id": "movie_id",
    "user_id": "user_id",
    "rating": "rating",
    "timestamp": "timestamp",
    "gender": "gender",
    "age": "age",
    "occupation": "occupation",
    "zip": "zip",
    "title_x": "title_x",
    "genres_x": "genres_x",
    "title_y": "title_y",
    "genres_y": "genres_y"
})

# The target schema expects title_x and genres_x as integers, but source0 and source2 do not have these columns.
# The only source with title and genres is s1, which after join is title_y and genres_y.
# The target examples show title_x and genres_x as integers, likely counts or encoded values.
# Since no source provides title_x and genres_x as integers, we can create them as counts per movie_id from s2.

# Create title_x and genres_x as counts of ratings per movie_id (integer)
counts = s2.groupby("movie_id").size().reset_index(name="count")
counts = counts.rename(columns={"count": "title_x"})
final = pd.merge(final, counts, on="movie_id", how="left")
final["genres_x"] = final["title_x"]

# Reorder columns to match target schema
final = final[[
    "movie_id", "user_id", "rating", "timestamp", "gender", "age", "occupation", "zip",
    "title_x", "genres_x", "title", "genres"
]]

# Rename title and genres to title_y and genres_y
final = final.rename(columns={"title": "title_y", "genres": "genres_y"})

# Convert columns to correct types
final["movie_id"] = final["movie_id"].astype(int)
final["user_id"] = final["user_id"].astype(int)
final["rating"] = final["rating"].astype(int)
final["timestamp"] = final["timestamp"].astype(int)
final["gender"] = final["gender"].map({"M":1, "F":2}).fillna(0).astype(int)
final["age"] = pd.to_numeric(final["age"], errors='coerce').fillna(0).astype(int)
final["occupation"] = pd.to_numeric(final["occupation"], errors='coerce').fillna(0).astype(int)
final["zip"] = final["zip"].astype(str).str.extract(r'(\d+)').fillna('0').astype(int)
final["title_x"] = final["title_x"].astype(int)
final["genres_x"] = final["genres_x"].astype(int)
final["title_y"] = final["title_y"].astype(str)
final["genres_y"] = final["genres_y"].astype(str)

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_93/target_multisource_mcts.csv", index=False)