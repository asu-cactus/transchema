import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_3.csv", index_col=0)

join_result = pd.merge(source3, source0, on="County", how="inner")

union_result = pd.concat([source1, source2], axis=0, ignore_index=True)

final = pd.merge(join_result, union_result, on="County", how="inner")

final = final[["County", "m1401", "m1403"]]

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_36/target_multisource_mcts.csv", index=False)