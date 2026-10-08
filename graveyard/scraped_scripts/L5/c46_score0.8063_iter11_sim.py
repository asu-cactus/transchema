import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_4.csv", index_col=0)

df = s4.merge(s0[['Cust_id', 'Customer_Name']], on='Cust_id', how='left')
df = df.merge(s2[['Ord_id']], on='Ord_id', how='left')
df = df.merge(s3[['Prod_id']], on='Prod_id', how='left')
df = df.merge(s1[['Ship_id']], on='Ship_id', how='left')

df['Ord_id_int'] = df['Ord_id'].str.extract(r'(\d+)').astype(float)
df['Prod_id_int'] = df['Prod_id'].str.extract(r'(\d+)').astype(float)
df['Ship_id_int'] = df['Ship_id'].str.extract(r'(\d+)').astype(float)

agg = df.groupby('Customer_Name').agg(
    Ord_id=('Ord_id_int', 'count'),
    Prod_id=('Prod_id_int', 'sum'),
    Ship_id=('Ship_id_int', 'sum')
).reset_index()

agg['Ord_id'] = agg['Ord_id'].astype(int)
agg['Prod_id'] = agg['Prod_id'].round().astype(int)
agg['Ship_id'] = agg['Ship_id'].round().astype(int)

agg = agg[['Customer_Name', 'Ord_id', 'Prod_id', 'Ship_id']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_46/target_multisource_mcts.csv", index=False)