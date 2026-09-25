import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_46/training_0.csv", index_col=0)

grouped = df0.groupby('Text Date', as_index=False).agg({'Water Use': 'sum', 'Power Use': 'sum'})

grouped['Date'] = grouped['Text Date']
grouped = grouped.drop(columns=['Text Date'])

grouped['Water Use'] = grouped['Water Use'].astype(float)
grouped['Power Use'] = grouped['Power Use'].astype(int)

grouped = grouped[['Date', 'Water Use', 'Power Use']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_46/target_multisource_mcts.csv", index=False)