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

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Ensure correct dtypes
df = df.astype({
    'admit': 'int64',
    'gre': 'int64',
    'gpa': 'float64',
    'prestige': 'int64'
})

# Group by admit and gre, aggregate gpa by mean, prestige by min
df_grouped = df.groupby(['admit', 'gre'], as_index=False).agg({
    'gpa': 'mean',
    'prestige': 'min'
})

# Cast columns to target types explicitly (prestige may become float after aggregation)
df_grouped = df_grouped.astype({
    'admit': 'int64',
    'gre': 'int64',
    'gpa': 'float64',
    'prestige': 'int64'
})

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_97/target_multisource_mcts.csv", index=False)