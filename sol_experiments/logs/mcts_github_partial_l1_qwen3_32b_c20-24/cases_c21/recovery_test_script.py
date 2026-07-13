import pandas as pd

source_path = "autopipeline-benchmarks/github-pipelines/length1_21/test_0.csv"
df = pd.read_csv(source_path, index_col=0)
result = df.groupby("Major_category")["Median"].mean().reset_index()
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_21/target_multisource_mcts_recovery_test_val.csv", index=False)