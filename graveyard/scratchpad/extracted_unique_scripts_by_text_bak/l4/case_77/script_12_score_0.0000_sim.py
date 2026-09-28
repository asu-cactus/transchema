import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_2.csv", index_col=0)

join_01 = pd.merge(source1, source0, left_on="name", right_on="school", how="inner")

final_join = pd.merge(join_01, source2, left_on="name", right_on="school", how="inner")

result = final_join[[
    "School ID",
    "name",
    "type",
    "size",
    "budget",
    "Average Math Score",
    "Average Reading Score",
    "Number Passing Math",
    "Number Passing Reading"
]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_77/target_multisource_mcts.csv", index=False)