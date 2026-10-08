import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_4.csv", index_col=0)

join_0 = pd.merge(s0, s4, on='Order_ID', how='inner')
join_1 = pd.merge(join_0, s2, left_on=['Ord_id', 'Ship_id'], right_on=['Ord_id', 'Ship_id'], how='inner')
join_2 = pd.merge(join_1, s1, on='Cust_id', how='inner')
join_3 = pd.merge(join_2, s3, on='Prod_id', how='inner')

grouped = join_3.groupby('Cust_id', as_index=False)['Profit'].sum()
result = grouped[['Profit']].copy()
result['Profit'] = result['Profit'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_86/target_multisource_mcts.csv", index=False)