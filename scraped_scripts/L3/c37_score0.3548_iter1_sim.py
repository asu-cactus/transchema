import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_3.csv", index_col=0)

union_result = pd.concat([source3, source0], ignore_index=True, sort=False)

join_result_1 = pd.merge(union_result, source1, on="County", how="outer")

join_result_2 = pd.merge(join_result_1, source2, on="County", how="outer")

result = join_result_2[["County", "r1401", "r1403"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_37/target_multisource_mcts.csv", index=False)