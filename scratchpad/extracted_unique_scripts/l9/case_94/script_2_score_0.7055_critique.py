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

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Ensure correct types before aggregation
df = df.astype({
    'admit': 'int64',
    'gre': 'int64',
    'gpa': 'float64',
    'prestige': 'int64'
})

# Group by leftmost non-float columns that uniquely identify rows, aggregate gpa by mean
df = df.groupby(['admit', 'gre', 'prestige'], as_index=False).agg({'gpa': 'mean'})

# Reorder columns to match target schema exactly
df = df[['admit', 'gre', 'gpa', 'prestige']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_94/target_multisource_mcts.csv", index=False)