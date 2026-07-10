import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_2.csv", index_col=0)

union_result = pd.concat([s1, s1], ignore_index=True)

join_result = pd.merge(union_result, s0, on="County", how="outer")

final_result = pd.merge(join_result, s2, on="County", how="outer")

final_result = final_result[["County", "m1401", "m1403"]]

final_result.to_csv("autopipeline-benchmarks/github-pipelines/length3_36/target_multisource_mcts.csv", index=False)