import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_7/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_7/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_7/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_7/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_7/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_7/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_7/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_7/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_7/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_7/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

# Ensure correct types
df = df.astype({
    'admit': 'int64',
    'gre': 'int64',
    'gpa': 'float64',
    'prestige': 'int64'
})

# Group by admit, gre, prestige and aggregate mean of gpa to remove duplicates and match target
df = df.groupby(['admit', 'gre', 'prestige'], as_index=False).agg({'gpa': 'mean'})

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_7/target_multisource_mcts.csv", index=False)