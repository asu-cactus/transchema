import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_7/test_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_7/test_1.csv", index_col=0)

result = pd.merge(df1, df0, on="city", how="inner")

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_7/target_multisource_mcts_recovery_test_val.csv", index=False)