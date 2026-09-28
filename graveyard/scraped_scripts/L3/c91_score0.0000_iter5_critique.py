import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_91/training_2.csv", index_col=0)

join_01 = pd.merge(source0, source1, how="inner", on="movie_id")
join_result = pd.merge(join_01, source2, how="inner", on="user_id")

grouped = join_result.groupby(['title', 'movie_id', 'video_release_date'], as_index=False).agg({
    'user_id': 'mean',
    'rating': 'mean',
    'unix_timestamp': 'mean',
    'age': 'mean'
})

target = grouped[[
    "title",
    "movie_id",
    "video_release_date",
    "user_id",
    "rating",
    "unix_timestamp",
    "age"
]]

target.to_csv("autopipeline-benchmarks/github-pipelines/length3_91/target_multisource_mcts.csv", index=False)