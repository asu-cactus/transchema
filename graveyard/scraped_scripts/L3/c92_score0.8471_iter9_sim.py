import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_2.csv", index_col=0)

agg = src2.groupby("movie_id").agg(
    user_id=("user_id", "mean"),
    rating=("rating", "mean"),
    unix_timestamp=("unix_timestamp", "mean")
).reset_index()

join_0 = pd.merge(src0, agg, how="inner", on="movie_id")

final = pd.merge(join_0, src1[["user_id", "age"]], how="left", on="user_id")

result = final[["title", "movie_id", "video_release_date", "user_id", "rating", "unix_timestamp", "age"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_92/target_multisource_mcts.csv", index=False)