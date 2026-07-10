import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_66/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_9.csv"
]

# Read all source tables
dfs = [pd.read_csv(p, index_col=0) for p in paths]

# Union all source tables
df_union = pd.concat(dfs, ignore_index=True)

# Group by admit, gre, prestige and aggregate mean on gpa
df_grouped = df_union.groupby(['admit', 'gre', 'prestige'], as_index=False).agg({'gpa': 'mean'})

# Ensure correct dtypes
df_grouped = df_grouped.astype({
    'admit': 'int64',
    'gre': 'int64',
    'gpa': 'float64',
    'prestige': 'int64'
})

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_66/target_multisource_mcts.csv", index=False)