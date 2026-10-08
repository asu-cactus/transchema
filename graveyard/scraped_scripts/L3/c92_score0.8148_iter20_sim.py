import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_2.csv", index_col=0)

agg = source2.groupby("movie_id").agg(
    user_id=("user_id", "nunique"),
    unix_timestamp=("unix_timestamp", "mean"),
    rating=("rating", "mean")
).reset_index()

joined_0 = pd.merge(source0, agg, how="inner", left_on="movie_id", right_on="movie_id")

joined = pd.merge(joined_0, source1, how="left", left_on="user_id", right_on="user_id")

result = pd.DataFrame()
result["title"] = joined["title"]
result["movie_id"] = joined["movie_id"].astype("Int64")
result["video_release_date"] = joined["video_release_date"].astype(float)
result["user_id"] = joined["user_id"].astype(float)
result["rating"] = joined["rating"].astype(float)
result["unix_timestamp"] = joined["unix_timestamp"].astype(float)
result["age"] = joined["age"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_92/target_multisource_mcts.csv", index=False)