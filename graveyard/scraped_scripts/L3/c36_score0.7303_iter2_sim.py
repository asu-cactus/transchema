import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_36/training_2.csv", index_col=0)

union_result = pd.concat([src1, src1], ignore_index=True)

join_result = pd.merge(union_result, src2, on="County", how="left")

final_join = pd.merge(join_result, src0, on="County", how="left")

final = final_join[["County", "m1401", "m1403"]]

final.to_csv("autopipeline-benchmarks/github-pipelines/length3_36/target_multisource_mcts.csv", index=False)