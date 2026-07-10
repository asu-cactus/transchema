import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_17/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_17/training_11.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df = df.astype({
    'tripduration': 'int64',
    'starttime': 'string',
    'stoptime': 'string',
    'start station id': 'Int64',
    'start station name': 'string',
    'start station latitude': 'float64',
    'start station longitude': 'float64',
    'end station id': 'Int64',
    'end station name': 'string',
    'end station latitude': 'float64',
    'end station longitude': 'float64',
    'bikeid': 'Int64',
    'usertype': 'string',
    'birth year': 'Int64',
    'gender': 'Int64'
})

# Group by primary key columns and aggregate by first to remove duplicates
df = df.groupby(['starttime', 'stoptime', 'bikeid'], as_index=False).agg({
    'tripduration': 'first',
    'start station id': 'first',
    'start station name': 'first',
    'start station latitude': 'first',
    'start station longitude': 'first',
    'end station id': 'first',
    'end station name': 'first',
    'end station latitude': 'first',
    'end station longitude': 'first',
    'usertype': 'first',
    'birth year': 'first',
    'gender': 'first'
})

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_17/target_multisource_mcts.csv", index=False)