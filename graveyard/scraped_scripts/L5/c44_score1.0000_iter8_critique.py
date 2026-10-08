import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_4.csv", index_col=0)

# Join all tables on their keys
r0 = pd.merge(s4, s0[['Ord_id']], on='Ord_id', how='inner')
r1 = pd.merge(r0, s1[['Cust_id', 'Customer_Segment']], on='Cust_id', how='inner')
r2 = pd.merge(r1, s2[['Prod_id']], on='Prod_id', how='inner')
r3 = pd.merge(r2, s3[['Ship_id']], on='Ship_id', how='inner')

# Group by Customer_Segment and aggregate counts of distinct Ord_id
agg = r3.groupby('Customer_Segment').agg(
    Ord_id=('Ord_id', 'nunique'),
    Prod_id=('Ord_id', 'nunique'),
    Ship_id=('Ord_id', 'nunique'),
    Cust_id=('Ord_id', 'nunique')
).reset_index()

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_44/target_multisource_mcts.csv", index=False)