import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_59/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_59/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_59/training_2.csv", index_col=0)

join_0_2 = pd.merge(source2, source0, on="movie_id", how="left")
join_all = pd.merge(join_0_2, source1, on="user_id", how="left")

target = join_all[[
    "user_id", "movie_id", "rating", "timestamp",
    "gender", "age", "occupation", "zip",
    "title", "genres"
]]

target.to_csv("autopipeline-benchmarks/github-pipelines/length2_59/target_multisource_mcts.csv", index=False)