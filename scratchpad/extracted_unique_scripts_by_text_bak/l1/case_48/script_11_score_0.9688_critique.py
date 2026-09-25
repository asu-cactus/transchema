import pandas as pd

df = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_48/training_0.csv', index_col=0)
df = df.rename(columns={'Text Date': 'Date'})
grouped = df.groupby('Date', as_index=False).agg({'Water Use': 'sum', 'Power Use': 'sum'})
grouped['Water Use'] = grouped['Water Use'].astype(float)
grouped['Power Use'] = grouped['Power Use'].astype(int)
grouped.to_csv('autopipeline-benchmarks/github-pipelines/length1_48/target_multisource_mcts.csv', index=False)