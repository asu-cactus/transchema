import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_2.csv", index_col=0)

union_result = pd.concat([src2, src2], ignore_index=True)

join_result = pd.merge(src1, union_result, on="County", how="inner")

final_join = pd.merge(join_result, src0, on="County", how="inner")

final = final_join[["County", "m1401", "m1403"]]

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_36/target_multisource_mcts.csv", index=False)