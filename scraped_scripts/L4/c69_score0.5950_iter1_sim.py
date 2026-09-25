import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_2.csv", index_col=0)

union_result = pd.concat([source1, source2], ignore_index=True)

merged = pd.merge(source0, union_result, on="user_id", how="inner")

merged = merged.astype({
    "user_id": "int64",
    "year_school": "string",
    "floor": "string",
    "party": "string",
    "libcon": "string",
    "fav_music": "string"
})

merged.to_csv("autopipeline-benchmarks/github-pipelines/length4_69/target_multisource_mcts.csv", index=False)