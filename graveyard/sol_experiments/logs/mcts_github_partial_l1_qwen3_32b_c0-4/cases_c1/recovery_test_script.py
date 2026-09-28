import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_1/test_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_1/test_1.csv", index_col=0)

grouped_source0 = source0.groupby("Student ID").first().reset_index()
result = grouped_source0.merge(source1, on="school_name", how="left")

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_1/target_multisource_mcts_recovery_test_val.csv", index=False)