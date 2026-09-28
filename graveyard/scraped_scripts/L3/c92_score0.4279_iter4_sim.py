import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_92/training_2.csv", index_col=0)

join_0_2 = pd.merge(source0, source2, how="inner", on="movie_id")
join_result = pd.merge(join_0_2, source1, how="inner", on="user_id")

result = join_result[[
    "title",
    "movie_id",
    "video_release_date",
    "user_id",
    "rating",
    "unix_timestamp",
    "age"
]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_92/target_multisource_mcts.csv", index=False)