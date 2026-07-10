import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_4.csv", index_col=0)

# Join Source4_31_0 and Source4_31_2 on County
result = s0.merge(s2, on="County", how="outer")

# Join with Source4_31_3 on County
result = result.merge(s3, on="County", how="outer")

# Join with Source4_31_4 on County
result = result.merge(s4, on="County", how="outer")

# Join with Source4_31_1 on County to ensure all counties appear
result = result.merge(s1, on="County", how="outer")

# Select columns in target schema order
result = result[['County', 'm1401', 'm1402', 'm1403', 'm1404']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_31/target_multisource_mcts.csv", index=False)