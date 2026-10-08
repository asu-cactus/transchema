import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_2.csv", index_col=0)

src0_renamed = src0.rename(columns={"m1403": "m1403"})
src2_renamed = src2.rename(columns={"m1401": "m1401"})

union_result = pd.concat([src0_renamed, src2_renamed], ignore_index=True, sort=False)

joined = pd.merge(union_result, src1, on="County", how="outer")

result = joined[["County", "m1401", "m1403"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_85/target_multisource_mcts.csv", index=False)