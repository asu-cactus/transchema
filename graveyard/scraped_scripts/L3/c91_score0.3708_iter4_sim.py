import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_2.csv", index_col=0)

agg = source1.merge(source2, on="user_id", how="inner")
agg = agg.groupby(["movie_id", "user_id"], as_index=False).agg(
    rating=("rating", "mean"),
    age=("age", "mean")
)

joined0 = agg.merge(source0, on="movie_id", how="inner")
final = joined0.merge(source1[["user_id", "unix_timestamp"]], on="user_id", how="inner")

final = final.rename(columns={
    "release_date": "video_release_date"
})

final = final[["title", "movie_id", "video_release_date", "user_id", "rating", "unix_timestamp", "age"]]

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_91/target_multisource_mcts.csv", index=False)