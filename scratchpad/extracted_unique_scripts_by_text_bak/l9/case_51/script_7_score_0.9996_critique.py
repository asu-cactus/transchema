import pandas as pd

# Read all source CSVs
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_51/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_51/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_51/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_51/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_51/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_51/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_51/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_51/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_51/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_51/training_9.csv", index_col=0)
s10 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_51/training_10.csv", index_col=0)
s11 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_51/training_11.csv", index_col=0)
s12 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_51/training_12.csv", index_col=0)
s13 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_51/training_13.csv", index_col=0)
s14 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_51/training_14.csv", index_col=0)

# Union all sources
result = pd.concat([s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14], ignore_index=True)

# Ensure column type matches target schema
result = result[['title']].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_51/target_multisource_mcts.csv", index=False)