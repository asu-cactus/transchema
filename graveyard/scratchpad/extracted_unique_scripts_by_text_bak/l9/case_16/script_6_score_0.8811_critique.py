import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_16/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_16/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_16/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_16/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_16/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_16/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_16/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_16/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_16/training_8.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Ensure correct types as strings
df = df.astype({
    'created_at': 'string',
    'text': 'string',
    'coordinates': 'string',
    'hashtags': 'string'
})

# Group by created_at and aggregate other columns by first non-null value
df = df.groupby('created_at', dropna=False, as_index=False).agg({
    'text': 'first',
    'coordinates': 'first',
    'hashtags': 'first'
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_16/target_multisource_mcts.csv", index=False)