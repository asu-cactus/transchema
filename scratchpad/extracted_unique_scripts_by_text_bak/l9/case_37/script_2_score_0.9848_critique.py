import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_9.csv", index_col=0)
s10 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_37/training_10.csv", index_col=0)

# Concatenate all dataframes vertically (UNION)
df = pd.concat([s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10], ignore_index=True)

# Ensure column name and type matches target schema
df = df.astype({'0': int})

# Output result
df.to_csv("autopipeline-benchmarks/github-pipelines/length9_37/target_multisource_mcts.csv", index=False)