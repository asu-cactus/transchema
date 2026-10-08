import pandas as pd

df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_10/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_10/training_1.csv", index_col=0)

df = pd.concat([df1, df2], ignore_index=True)
df = df[['city', 'driver_count']]
df['driver_count'] = df['driver_count'].astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length2_10/target_multisource_mcts.csv", index=False)