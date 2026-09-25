import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_3.csv", index_col=0)

join_1 = pd.merge(source1, source2, on="County", how="outer")
join_2 = pd.merge(join_1, source0, on="County", how="outer")
join_3 = pd.merge(join_2, source3, on="County", how="inner")

result = join_3[["County", "m1401", "m1403"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_36/target_multisource_mcts.csv", index=False)