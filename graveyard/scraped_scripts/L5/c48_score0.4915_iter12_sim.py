import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_4.csv", index_col=0)

agg = s4.groupby(['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id'], as_index=False).agg({'Sales':'sum', 'Discount':'sum'})

join1 = pd.merge(agg, s0[['Ord_id', 'Order_Date']], on='Ord_id', how='left')
join2 = pd.merge(join1, s3[['Prod_id']], on='Prod_id', how='left')
join3 = pd.merge(join2, s1[['Ship_id']], on='Ship_id', how='left')
join4 = pd.merge(join3, s2[['Cust_id']], on='Cust_id', how='left')

join4['Sales'] = join4['Sales'].round().astype('Int64')
join4['Discount'] = join4['Discount'].round().astype('Int64')

result = join4[['Order_Date', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_48/target_multisource_mcts.csv", index=False)