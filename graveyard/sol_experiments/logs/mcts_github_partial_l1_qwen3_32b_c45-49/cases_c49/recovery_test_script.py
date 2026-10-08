import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_49/test_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_49/test_1.csv", index_col=0)

union_df = pd.concat([source0, source1], ignore_index=True)
union_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_49/target_multisource_mcts_recovery_test_val.csv")