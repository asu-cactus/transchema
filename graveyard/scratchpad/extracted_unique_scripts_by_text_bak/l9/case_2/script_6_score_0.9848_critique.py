import pandas as pd

# Load all source tables
source_0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_2/training_0.csv", index_col=0)
source_1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_2/training_1.csv", index_col=0)
source_2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_2/training_2.csv", index_col=0)
source_3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_2/training_3.csv", index_col=0)
source_4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_2/training_4.csv", index_col=0)
source_5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_2/training_5.csv", index_col=0)
source_6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_2/training_6.csv", index_col=0)
source_7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_2/training_7.csv", index_col=0)
source_8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_2/training_8.csv", index_col=0)
source_9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_2/training_9.csv", index_col=0)
source_10 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_2/training_10.csv", index_col=0)

# Union all source tables
union_all = pd.concat([
    source_0,
    source_1,
    source_2,
    source_3,
    source_4,
    source_5,
    source_6,
    source_7,
    source_8,
    source_9,
    source_10
], ignore_index=True)

# Ensure the column '0' is integer type as per target schema
union_all['0'] = union_all['0'].astype(int)

# Save the result
union_all.to_csv("autopipeline-benchmarks/github-pipelines/length9_2/target_multisource_mcts.csv", index=False)