import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_4.csv", index_col=0)

join_0 = pd.merge(df2, df0, how='inner', left_on='Ship_id', right_on='Ship_id')
join_1 = pd.merge(join_0, df1, how='inner', left_on='Prod_id', right_on='Prod_id')
join_2 = pd.merge(join_1, df3, how='inner', left_on='Cust_id', right_on='Cust_id')
join_3 = pd.merge(join_2, df4, how='inner', left_on='Ord_id', right_on='Ord_id')

result = join_3[['Profit']].copy()
result['Profit'] = result['Profit'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_87/target_multisource_mcts.csv", index=False)