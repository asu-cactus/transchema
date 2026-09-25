import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_9/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_9/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_9/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_9/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_9/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_9/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_9/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_9/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_9/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_9/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Group by leftmost integer columns except the float column 'gpa'
# Aggregate 'gpa' by mean
df = df.groupby(['admit', 'gre', 'prestige'], as_index=False).agg({'gpa': 'mean'})

df = df.astype({
    'admit': 'int64',
    'gre': 'int64',
    'gpa': 'float64',
    'prestige': 'int64'
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_9/target_multisource_mcts.csv", index=False)