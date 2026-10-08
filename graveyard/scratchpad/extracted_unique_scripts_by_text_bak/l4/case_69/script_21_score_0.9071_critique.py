import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_2.csv", index_col=0)

# Join source0 and source1 on user_id
merged_01 = pd.merge(source0, source1, on="user_id", how="inner")

# Join the above result with source2 on user_id
merged = pd.merge(merged_01, source2, on="user_id", how="inner")

# Select columns in target schema order
merged = merged[['user_id', 'year_school', 'floor', 'party', 'libcon', 'fav_music']]

merged.to_csv("autopipeline-benchmarks/github-pipelines/length4_69/target_multisource_mcts.csv", index=False)