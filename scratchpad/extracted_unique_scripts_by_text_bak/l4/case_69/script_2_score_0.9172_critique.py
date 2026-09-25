import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_2.csv", index_col=0)

join_01 = pd.merge(source0, source1, on="user_id", how="left")
final = pd.merge(join_01, source2, on="user_id", how="left")

final = final[['user_id', 'year_school', 'floor', 'party', 'libcon', 'fav_music']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length4_69/target_multisource_mcts.csv", index=False)