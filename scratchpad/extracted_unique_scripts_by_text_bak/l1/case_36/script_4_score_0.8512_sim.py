import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_36/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_36/training_1.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True)

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

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_36/target_multisource_mcts.csv", index=False)