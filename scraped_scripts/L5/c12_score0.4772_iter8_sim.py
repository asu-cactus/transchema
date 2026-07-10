import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_4.csv", index_col=0)

df = source4.merge(source0[['Ship_id', 'Ship_Mode']], on='Ship_id', how='inner')
df = df.merge(source1[['Ord_id', 'Order_Priority']], on='Ord_id', how='inner')
df = df.merge(source2[['Cust_id']], on='Cust_id', how='inner')
df = df.merge(source3[['Prod_id']], on='Prod_id', how='inner')

df = df[['Order_Priority', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

df['Ord_id'] = df['Ord_id'].str.extract('(\d+)').astype(int)
df['Prod_id'] = df['Prod_id'].str.extract('(\d+)').astype(int)
df['Ship_id'] = df['Ship_id'].str.extract('(\d+)').astype(int)
df['Cust_id'] = df['Cust_id'].str.extract('(\d+)').astype(int)
df['Sales'] = df['Sales'].round().astype(int)
df['Discount'] = (df['Discount'] * 100).round().astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_12/target_multisource_mcts.csv", index=False)