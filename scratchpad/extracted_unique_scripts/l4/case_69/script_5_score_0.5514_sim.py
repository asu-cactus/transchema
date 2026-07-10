import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_2.csv", index_col=0)

union_result = pd.concat([source1, source2], axis=0, ignore_index=True, sort=False)

merged = pd.merge(source0, union_result, on="user_id", how="inner")

target = merged[['user_id', 'year_school', 'floor', 'party', 'libcon', 'fav_music']]

target.to_csv("autopipeline-benchmarks/github-pipelines/length4_69/target_multisource_mcts.csv", index=False)