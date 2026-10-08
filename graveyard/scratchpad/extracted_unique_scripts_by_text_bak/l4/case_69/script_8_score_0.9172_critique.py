import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_2.csv", index_col=0)

# Join source1 and source2 on user_id with outer join to preserve all users
join_1_2 = pd.merge(source1, source2, on="user_id", how="outer")

# Join source0 with the above join on user_id with right join to preserve all rows from source0
final_join = pd.merge(source0, join_1_2, on="user_id", how="left")

# Group by user_id to ensure uniqueness (no aggregation needed as columns are unique per user_id)
final = final_join.groupby("user_id", as_index=False).first()

# Select columns in target schema order
final = final[["user_id", "year_school", "floor", "party", "libcon", "fav_music"]]

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_69/target_multisource_mcts.csv", index=False)