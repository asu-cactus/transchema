import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_37/training_3.csv", index_col=0)

union_result = pd.concat([s0, s3], ignore_index=True, sort=False)

join_result = pd.merge(union_result, s1, on="County", how="outer")

final_join = pd.merge(join_result, s2, on="County", how="outer")

result = final_join[["County", "r1401", "r1403"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_37/target_multisource_mcts.csv", index=False)