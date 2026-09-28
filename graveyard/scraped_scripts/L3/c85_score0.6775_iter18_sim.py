import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_3.csv", index_col=0)

join_0_2 = pd.merge(s0, s2, on="County", how="outer")
join_0_2_1 = pd.merge(join_0_2, s1, on="County", how="outer")
full_join = pd.merge(join_0_2_1, s3, on="County", how="outer")

result = full_join[["County", "m1401", "m1403"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_85/target_multisource_mcts.csv", index=False)