import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_4.csv", index_col=0)

join1 = pd.merge(df4, df0[['Customer_Name', 'Cust_id']], on='Cust_id', how='inner')
join2 = pd.merge(join1, df2[['Ord_id']], on='Ord_id', how='inner')
join3 = pd.merge(join2, df3[['Prod_id']], on='Prod_id', how='inner')

result = join3[['Customer_Name', 'Ord_id', 'Prod_id', 'Ship_id']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_46/target_multisource_mcts.csv", index=False)