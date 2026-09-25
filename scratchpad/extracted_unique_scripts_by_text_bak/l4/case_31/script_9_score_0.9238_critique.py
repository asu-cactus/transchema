import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_4.csv", index_col=0)

join_12 = pd.merge(source1, source2, on="County", how="inner")
join_123 = pd.merge(join_12, source3, on="County", how="inner")
join_1234 = pd.merge(join_123, source4, on="County", how="inner")
join_12340 = pd.merge(join_1234, source0, on="County", how="inner")

target = join_12340[["County", "m1401", "m1402", "m1403", "m1404"]]

target.to_csv("autopipeline-benchmarks/github-pipelines/length4_31/target_multisource_mcts.csv", index=False)