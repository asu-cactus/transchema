import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_96/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_96/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_96/training_2.csv", index_col=0)

merged_1_2 = pd.merge(source2, source1, left_on="movie id", right_on="movie id", how="inner")
final = pd.merge(merged_1_2, source0, left_on="user id", right_on="user id", how="inner")

final = final[[
    "movie title", "movie id", "release date", "video release date", "IMDb URL", "unknown", "Action", "Adventure",
    "Animation", "Childrens", "Comedy", "Crime", "Documentary", "Drama", "Fantasy", "Film-Noir", "Horror", "Musical",
    "Mystery", "Romance ", "Sci-Fi", "Thriller", "War", "Western", "user id", "rating", "timestamp", "age", "gender",
    "occupation", "zip code"
]]

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_96/target_multisource_mcts.csv", index=False)