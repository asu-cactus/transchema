import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_95/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, on=['customer_id', 'date'])

result = joined.groupby('customer_id', as_index=False).first()[['customer_id', 'date']]

result['customer_id'] = result['customer_id'].astype(int)
result['date'] = result['date'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_95/target_multisource_mcts.csv", index=False)