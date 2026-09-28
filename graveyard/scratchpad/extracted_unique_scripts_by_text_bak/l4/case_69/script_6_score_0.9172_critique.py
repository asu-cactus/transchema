import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_2.csv", index_col=0)

# Left join source1 to source0 on user_id to keep all user_ids from source0
joined_0_1 = pd.merge(source0, source1, on="user_id", how="left")

# Left join source2 to the above result on user_id
final_join = pd.merge(joined_0_1, source2, on="user_id", how="left")

# Select columns in target schema order
final = final_join[["user_id", "year_school", "floor", "party", "libcon", "fav_music"]]

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_69/target_multisource_mcts.csv", index=False)