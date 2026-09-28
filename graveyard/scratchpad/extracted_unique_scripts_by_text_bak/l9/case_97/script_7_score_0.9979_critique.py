import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_97/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_97/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_97/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_97/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_97/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_97/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_97/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_97/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_97/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_97/training_9.csv"
]

# Read all source tables with index_col=0 to ignore the first index column
dfs = [pd.read_csv(p, index_col=0) for p in paths]

# UNION all source tables by concatenation
df = pd.concat(dfs, ignore_index=True)

# Cast columns to target schema types
df = df.astype({
    'admit': 'int64',
    'gre': 'int64',
    'gpa': 'float64',
    'prestige': 'int64'
})

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length9_97/target_multisource_mcts.csv", index=False)