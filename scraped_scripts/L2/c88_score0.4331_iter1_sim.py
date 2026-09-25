import pandas as pd

df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_88/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_88/training_1.csv", index_col=0)

df = pd.concat([df1, df2], ignore_index=True)

df = df[['city', 'fare', 'ride_id']]

df['fare'] = df['fare'].astype(float)
df['ride_id'] = df['ride_id'].astype(int)
df['city'] = df['city'].astype(str)

df.to_csv("autopipeline-benchmarks/github-pipelines/length2_88/target_multisource_mcts.csv", index=False)