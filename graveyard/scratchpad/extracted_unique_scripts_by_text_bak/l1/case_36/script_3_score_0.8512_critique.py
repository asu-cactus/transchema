import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_36/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_36/training_1.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True)

# Ensure correct dtypes matching target schema
df['tripduration'] = df['tripduration'].astype(int)
df['start station id'] = df['start station id'].astype(int)
df['end station id'] = df['end station id'].astype(int)
df['bikeid'] = df['bikeid'].astype(int)
df['birth year'] = df['birth year'].astype(int)
df['gender'] = df['gender'].astype(int)

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length1_36/target_multisource_mcts.csv", index=False)