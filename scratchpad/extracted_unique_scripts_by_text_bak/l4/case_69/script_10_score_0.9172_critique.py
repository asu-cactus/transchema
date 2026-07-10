import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_2.csv", index_col=0)

# Left join source1 to source0 to keep all rows from source0
join_01 = pd.merge(source0, source1, on="user_id", how="left")

# Left join source2 to the previous join result to keep all rows from source0
final_df = pd.merge(join_01, source2, on="user_id", how="left")

final_df = final_df.astype({
    "user_id": "int64",
    "year_school": "string",
    "floor": "string",
    "party": "string",
    "libcon": "string",
    "fav_music": "string"
})

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_69/target_multisource_mcts.csv", index=False)