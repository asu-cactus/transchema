import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_83/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_83/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_83/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_83/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_83/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_83/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_83/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_83/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_83/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_83/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

# Union all source tables
union_df = pd.concat(dfs, ignore_index=True)

# Remove duplicate rows to match target row count
union_df = union_df.drop_duplicates()

# Ensure correct dtypes as per target schema
union_df = union_df.astype({
    'admit': 'int64',
    'gre': 'int64',
    'gpa': 'float64',
    'prestige': 'int64'
})

union_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_83/target_multisource_mcts.csv", index=False)