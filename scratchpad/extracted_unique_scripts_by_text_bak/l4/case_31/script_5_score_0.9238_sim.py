import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_4.csv", index_col=0)

join_01 = pd.merge(source1, source0, on="County", how="inner")
join_012 = pd.merge(join_01, source2, on="County", how="inner")
join_0123 = pd.merge(join_012, source3, on="County", how="inner")
join_01234 = pd.merge(join_0123, source4, on="County", how="inner")

result = join_01234.groupby(["County", "m1401", "m1402", "m1403", "m1404"], as_index=False).size()
result = result.drop(columns=["size"])

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_31/target_multisource_mcts.csv", index=False)