import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_3.csv", index_col=0)

union_result = pd.concat([s0, s2], ignore_index=True)
join_result = pd.merge(union_result, s1, on="County", how="outer")
final_join = pd.merge(join_result, s3, on="County", how="outer")

final = final_join[["County", "m1401", "m1403"]]

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_85/target_multisource_mcts.csv", index=False)