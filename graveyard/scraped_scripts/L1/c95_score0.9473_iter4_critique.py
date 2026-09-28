import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_95/training_0.csv", index_col=0)
df0['date'] = pd.to_datetime(df0['date'])
result = df0.groupby('customer_id', as_index=False)['date'].max()
result['date'] = result['date'].dt.strftime('%Y-%m-%d')
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_95/target_multisource_mcts.csv", index=False)