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

# Ensure columns are in the target schema order and types
target_columns = [
    'tripduration', 'starttime', 'stoptime', 'start station id', 'start station name',
    'start station latitude', 'start station longitude', 'end station id', 'end station name',
    'end station latitude', 'end station longitude', 'bikeid', 'usertype', 'birth year', 'gender'
]

df = df[target_columns]

df['tripduration'] = df['tripduration'].astype(int)
df['starttime'] = df['starttime'].astype(str)
df['stoptime'] = df['stoptime'].astype(str)
df['start station id'] = df['start station id'].astype(int)
df['start station name'] = df['start station name'].astype(str)
df['start station latitude'] = df['start station latitude'].astype(float)
df['start station longitude'] = df['start station longitude'].astype(float)
df['end station id'] = df['end station id'].astype(int)
df['end station name'] = df['end station name'].astype(str)
df['end station latitude'] = df['end station latitude'].astype(float)
df['end station longitude'] = df['end station longitude'].astype(float)
df['bikeid'] = df['bikeid'].astype(int)
df['usertype'] = df['usertype'].astype(str)
df['birth year'] = df['birth year'].astype(int)
df['gender'] = df['gender'].astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_17/target_multisource_mcts.csv", index=False)