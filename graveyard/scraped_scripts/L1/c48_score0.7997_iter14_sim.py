import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_48/training_0.csv", index_col=0)
grouped = df0.groupby('Value Date', as_index=False).agg({'Water Use':'mean', 'Power Use':'mean'})
grouped['Date'] = grouped['Value Date']
grouped['Water Use'] = grouped['Water Use'].astype(float)
grouped['Power Use'] = grouped['Power Use'].round().astype(int)
result = grouped[['Date', 'Water Use', 'Power Use']]
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_48/target_multisource_mcts.csv", index=False)