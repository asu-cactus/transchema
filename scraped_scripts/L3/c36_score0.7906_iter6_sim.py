import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_3.csv", index_col=0)

union_result = pd.concat([src3, src3], ignore_index=True)

join_result_1 = pd.merge(union_result, src1, on="County", how="inner")

join_result_2 = pd.merge(join_result_1, src2, on="County", how="inner")

target = join_result_2[["County", "m1401", "m1403"]]

target.to_csv("autopipeline-benchmarks/github-pipelines/length3_36/target_multisource_mcts.csv", index=False)