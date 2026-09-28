import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_2.csv", index_col=0)

merged_2_1 = pd.merge(source2, source1, on="user_id", how="inner")
merged_all = pd.merge(merged_2_1, source0[['movie_id', 'title', 'video_release_date']], on="movie_id", how="inner")

grouped = merged_all.groupby("title").agg(
    movie_id_count=pd.NamedAgg(column="movie_id", aggfunc="count"),
    unix_timestamp_avg=pd.NamedAgg(column="unix_timestamp", aggfunc="mean"),
    age_max=pd.NamedAgg(column="age", aggfunc="max"),
).reset_index()

# The target schema is:
# ['title': string, 'movie_id': integer, 'video_release_date': float, 'user_id': float, 'rating': float, 'unix_timestamp': float, 'age': float]
# We need to produce a table with these columns.
# The partial plan aggregates counts and averages but the target examples show averages for user_id, rating, unix_timestamp, age per title.
# So instead of the partial plan's aggregation, we should aggregate the relevant columns by title with mean for user_id, rating, unix_timestamp, age.
# movie_id and video_release_date come from source0, but movie_id is integer and video_release_date is float (NaN allowed).
# We can take the first movie_id and video_release_date per title (assuming title uniquely identifies movie_id).

agg = merged_all.groupby("title").agg(
    movie_id=('movie_id', 'first'),
    video_release_date=('video_release_date', 'first'),
    user_id=('user_id', 'mean'),
    rating=('rating', 'mean'),
    unix_timestamp=('unix_timestamp', 'mean'),
    age=('age', 'mean')
).reset_index()

agg = agg[['title', 'movie_id', 'video_release_date', 'user_id', 'rating', 'unix_timestamp', 'age']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_92/target_multisource_mcts.csv", index=False)