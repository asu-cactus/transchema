import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_31/training_4.csv", index_col=0)

# Start from Source1 (dimension table with County only)
result = pd.merge(source1, source2, on="County", how="left")
result = pd.merge(result, source3, on="County", how="left")
result = pd.merge(result, source4, on="County", how="left")
result = pd.merge(result, source0, on="County", how="left")

# Select columns in target schema order
result = result[["County", "m1401", "m1402", "m1403", "m1404"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_31/target_multisource_mcts.csv", index=False)