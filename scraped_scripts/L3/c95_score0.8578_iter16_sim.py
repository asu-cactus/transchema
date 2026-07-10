import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_95/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_95/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_95/training_2.csv", index_col=0)

merged_1_2 = pd.merge(source1, source2, on="user_id", how="inner")

grouped = merged_1_2.groupby(["sex", "occupation"]).agg(
    count_movie_id=("movie_id", "count"),
    avg_rating=("rating", "mean")
).reset_index()

# The partial plan says group by sex, release_date, occupation, but release_date is from source0, so we need to join source1+2 with source0 first on movie_id to get release_date
# But source1+2 merged has no movie_id release_date, so we need to join source1 with source0 on movie_id first to get release_date, then join with source2 on user_id

# Join source1 and source0 on movie_id to get release_date
source1_0 = pd.merge(source1, source0[["movie_id", "release_date", "title"]], on="movie_id", how="inner")

# Join with source2 on user_id to get sex and occupation
full_merged = pd.merge(source1_0, source2[["user_id", "sex", "occupation"]], on="user_id", how="inner")

# Now group by sex, release_date, occupation as per partial plan
grouped_full = full_merged.groupby(["sex", "release_date", "occupation", "movie_id", "title"]).agg(
    count_movie_id=("movie_id", "count"),
    avg_rating=("rating", "mean")
).reset_index()

# The target schema is movie_id, title, F, M
# We want average rating per sex (F and M) per movie_id and title
# Pivot sex to columns F and M with avg_rating as values
pivot = grouped_full.pivot_table(index=["movie_id", "title"], columns="sex", values="avg_rating", aggfunc='first').reset_index()

# Rename columns to match target schema
pivot = pivot.rename(columns={"F": "F", "M": "M"})

# Ensure columns order and types
pivot = pivot[["movie_id", "title", "F", "M"]]
pivot["movie_id"] = pivot["movie_id"].astype(int)
pivot["title"] = pivot["title"].astype(str)
pivot["F"] = pivot["F"].astype(float)
pivot["M"] = pivot["M"].astype(float)

pivot.to_csv("autopipeline-benchmarks/github-pipelines/length3_95/target_multisource_mcts.csv", index=False)