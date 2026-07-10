import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_82/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_9.csv"
]

# Read all source CSVs with index_col=0 to ignore the first index column
dfs = [pd.read_csv(p, index_col=0) for p in paths]

# UNION all source tables by concatenation
union_result = pd.concat(dfs, ignore_index=True)

# Ensure correct dtypes as per target schema
union_result = union_result.astype({
    'admit': 'int64',
    'gre': 'int64',
    'gpa': 'float64',
    'prestige': 'int64'
})

# Write the final output
union_result.to_csv("autopipeline-benchmarks/github-pipelines/length9_82/target_multisource_mcts.csv", index=False)