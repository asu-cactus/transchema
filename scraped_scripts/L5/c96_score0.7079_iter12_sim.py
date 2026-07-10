import pandas as pd

df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_96/training_2.csv", index_col=0)
result = pd.DataFrame()
result['Profit'] = [df2['Profit'].count(), df2['Profit'].mean(), df2['Profit'].min(), df2['Profit'].max()]
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_96/target_multisource_mcts.csv", index=False)