import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_62/training_0.csv", index_col=0)
grouped = df0.groupby('Text Date', as_index=False).agg({'Water Use': 'sum', 'Power Use': 'sum'})
grouped.rename(columns={'Text Date': 'Month'}, inplace=True)
grouped['Water Use'] = grouped['Water Use'].astype(float)
grouped['Power Use'] = grouped['Power Use'].astype(int)
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_62/target_multisource_mcts.csv", index=False)