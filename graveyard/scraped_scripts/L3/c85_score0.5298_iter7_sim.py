import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_85/training_3.csv", index_col=0)

joined_2_3 = pd.merge(source2, source3, on="County", how="inner")

union_2_0 = pd.concat([source2, source0], ignore_index=True, sort=False)

joined_union_3 = pd.merge(union_2_0, source3, on="County", how="inner")

final_join = pd.merge(joined_union_3, source1, on="County", how="inner")

result = final_join[["County", "m1401", "m1403"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_85/target_multisource_mcts.csv", index=False)