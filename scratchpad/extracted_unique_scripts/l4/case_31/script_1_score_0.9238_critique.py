import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_4.csv", index_col=0)

result_0 = pd.merge(source1, source0, on="County", how="inner")
result_1 = pd.merge(result_0, source2, on="County", how="inner")
result_2 = pd.merge(result_1, source3, on="County", how="inner")
result_3 = pd.merge(result_2, source4, on="County", how="inner")

target = result_3[["County", "m1401", "m1402", "m1403", "m1404"]]

target.to_csv("autopipeline-benchmarks/github-pipelines/length4_31/target_multisource_mcts.csv")