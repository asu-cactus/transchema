import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_94/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_94/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_94/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_94/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_94/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_94/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_94/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_94/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_94/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_94/training_9.csv"
]

# Read all source tables with index_col=0 to ignore the first column (index)
dfs = [pd.read_csv(p, index_col=0) for p in paths]

# UNION all source tables by concatenation
df = pd.concat(dfs, ignore_index=True)

# Ensure correct dtypes matching target schema
df = df.astype({
    'admit': 'int64',
    'gre': 'int64',
    'gpa': 'float64',
    'prestige': 'int64'
})

# Write the combined dataframe to the target CSV file
df.to_csv("autopipeline-benchmarks/github-pipelines/length9_94/target_multisource_mcts.csv", index=False)