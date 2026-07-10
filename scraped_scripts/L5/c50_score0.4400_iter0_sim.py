import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_2.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_4.csv", index_col=0)

df0['Ship_id'] = df0['Ship_id'].astype(str)
df1['Ord_id'] = df1['Ord_id'].astype(str)
df2['Prod_id'] = df2['Prod_id'].astype(str)
df4['Ord_id'] = df4['Ord_id'].astype(str)
df4['Prod_id'] = df4['Prod_id'].astype(str)
df4['Ship_id'] = df4['Ship_id'].astype(str)

join_0 = pd.merge(df4, df0[['Ship_Date', 'Ship_id']], on='Ship_id', how='inner')
join_1 = pd.merge(join_0, df1[['Ord_id', 'Order_Date']], on='Ord_id', how='inner')
join_2 = pd.merge(join_1, df2[['Prod_id']], on='Prod_id', how='inner')

join_2['Ship_Date'] = join_2['Ship_Date'].astype(str)
join_2['Ord_id'] = join_2['Ord_id'].str.extract(r'(\d+)').astype(int)
join_2['Prod_id'] = join_2['Prod_id'].str.extract(r'(\d+)').astype(int)
join_2['Ship_id'] = join_2['Ship_id'].str.extract(r'(\d+)').astype(int)

result = join_2.groupby(['Ship_Date', 'Ord_id', 'Prod_id', 'Ship_id'], as_index=False).size()
result = result.drop(columns='size')

result = result[['Ship_Date', 'Ord_id', 'Prod_id', 'Ship_id']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_50/target_multisource_mcts.csv", index=False)