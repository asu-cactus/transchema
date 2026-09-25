import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_44/training_4.csv", index_col=0)

# Join Source4 with Source0 on Ord_id
join_0_4 = pd.merge(source4, source0[['Ord_id']], on='Ord_id', how='inner')

# Join with Source1 on Cust_id to get Customer_Segment
join_1 = pd.merge(join_0_4, source1[['Cust_id', 'Customer_Segment']], on='Cust_id', how='inner')

# Join with Source2 on Prod_id
join_2 = pd.merge(join_1, source2[['Prod_id']], on='Prod_id', how='inner')

# Join with Source3 on Ship_id
join_3 = pd.merge(join_2, source3[['Ship_id']], on='Ship_id', how='inner')

# Group by Customer_Segment and aggregate counts of distinct IDs
result = join_3.groupby('Customer_Segment').agg(
    Ord_id=('Ord_id', 'nunique'),
    Prod_id=('Prod_id', 'nunique'),
    Ship_id=('Ship_id', 'nunique'),
    Cust_id=('Cust_id', 'nunique')
).reset_index()

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_44/target_multisource_mcts.csv", index=False)