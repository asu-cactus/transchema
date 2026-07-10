import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_2.csv", index_col=0)

source0 = source0.rename(columns={"m1403": "m1403"})
source1 = source1.rename(columns={"m1402": "m1403"})

union_result = pd.concat([source0, source1], ignore_index=True)

result = pd.merge(union_result, source2, on="County", how="inner")

result = result[["County", "m1401", "m1403"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_85/target_multisource_mcts.csv", index=False)