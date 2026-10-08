import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_2.csv", index_col=0)

joined_1_2 = pd.merge(source1, source2, on="user_id", how="outer")
final_join = pd.merge(joined_1_2, source0, on="user_id", how="outer")

result = final_join[["user_id", "year_school", "floor", "party", "libcon", "fav_music"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_69/target_multisource_mcts.csv")