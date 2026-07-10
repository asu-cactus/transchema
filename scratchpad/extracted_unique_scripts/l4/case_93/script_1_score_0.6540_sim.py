import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_2.csv", index_col=0)

join_1 = pd.merge(s2, s1, on="movie_id", how="inner")
join_2 = pd.merge(join_1, s0, on="user_id", how="inner")

join_2["gender"] = join_2["gender"].map({"M":1, "F":0}).fillna(0).astype(int)
join_2["age"] = pd.to_numeric(join_2["age"], errors="coerce").fillna(0).astype(int)
join_2["occupation"] = pd.to_numeric(join_2["occupation"], errors="coerce").fillna(0).astype(int)
join_2["zip"] = join_2["zip"].astype(str).str.extract(r'(\d+)').fillna("0").astype(int)

join_2 = join_2.rename(columns={
    "title_x": "title_x",  # no title_x in join_2 yet, so we create them by duplicating title and genres from s1 and s1 again
    "genres_x": "genres_x",
    "title_y": "title_y",
    "genres_y": "genres_y"
})

# The target schema requires title_x, genres_x as integer, and title_y, genres_y as string.
# We have only one title and genres from s1, so to produce title_x, genres_x as integer, we encode them as categorical codes.
# title_y and genres_y remain as string from s1.

join_2["title_y"] = join_2["title"]
join_2["genres_y"] = join_2["genres"]

join_2["title_x"] = join_2["title"].astype("category").cat.codes + 1
join_2["genres_x"] = join_2["genres"].astype("category").cat.codes + 1

final_cols = ["movie_id", "user_id", "rating", "timestamp", "gender", "age", "occupation", "zip",
              "title_x", "genres_x", "title_y", "genres_y"]

result = join_2[final_cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_93/target_multisource_mcts.csv", index=False)