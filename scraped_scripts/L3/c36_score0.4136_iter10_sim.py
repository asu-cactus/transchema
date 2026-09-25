import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_3.csv", index_col=0)

union_1_2 = pd.concat([s1, s2], ignore_index=True, sort=False)

join_1 = pd.merge(union_1_2, s0, on="County", how="outer")

final_join = pd.merge(join_1, s3, on="County", how="outer")

final = final_join[["County", "m1401", "m1403"]]

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_36/target_multisource_mcts.csv", index=False)