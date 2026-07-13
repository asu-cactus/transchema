import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_51/test_0.csv")
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_51/test_1.csv")

joined = source0.merge(source1, on="school_name", how="inner")
joined.to_csv("autopipeline-benchmarks/github-pipelines/length1_51/target_multisource_mcts_recovery_test_val.csv", index=False)