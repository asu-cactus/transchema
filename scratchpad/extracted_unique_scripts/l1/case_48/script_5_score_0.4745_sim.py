import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_48/training_0.csv", index_col=0)
df0 = df0[['Text Date', 'Water Use', 'Power Use']]
df0 = df0.rename(columns={'Text Date': 'Date'})
df0['Water Use'] = df0['Water Use'].astype(float)
df0['Power Use'] = df0['Power Use'].astype(int)
df0 = df0[['Date', 'Water Use', 'Power Use']]

df0.to_csv("autopipeline-benchmarks/github-pipelines/length1_48/target_multisource_mcts.csv", index=False)