import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_2.csv", index_col=0)

union_1_2 = pd.concat([src1, src2], ignore_index=True, sort=False)

merged = pd.merge(union_1_2, src0, on="user_id", how="inner")

result = merged[['user_id', 'year_school', 'floor', 'party', 'libcon', 'fav_music']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_69/target_multisource_mcts.csv", index=False)