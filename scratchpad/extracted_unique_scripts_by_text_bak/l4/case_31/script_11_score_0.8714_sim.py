import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_0.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_4.csv", index_col=0)

join_1 = pd.merge(source2, source0, on="County", how="inner")
join_2 = pd.merge(join_1, source3, on="County", how="inner")
join_3 = pd.merge(join_2, source4, on="County", how="inner")

target = join_3.groupby(['County', 'm1401', 'm1402', 'm1403', 'm1404'], as_index=False).size()
target = target.drop(columns='size')

target.to_csv("autopipeline-benchmarks/github-pipelines/length4_31/target_multisource_mcts.csv", index=False)