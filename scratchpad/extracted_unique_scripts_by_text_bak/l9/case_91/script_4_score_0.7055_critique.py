import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_91/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_91/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_91/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_91/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_91/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_91/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_91/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_91/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_91/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_91/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Group by the leftmost integer columns and aggregate gpa by mean
df_grouped = df.groupby(['admit', 'gre', 'prestige'], as_index=False).agg({'gpa': 'mean'})

# Ensure correct dtypes
df_grouped = df_grouped.astype({
    'admit': 'int64',
    'gre': 'int64',
    'gpa': 'float64',
    'prestige': 'int64'
})

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_91/target_multisource_mcts.csv", index=False)