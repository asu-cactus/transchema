import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_4.csv", index_col=0)

df = pd.merge(source4, source0[['Ship_id', 'Ship_Date']], on='Ship_id', how='inner')
df = pd.merge(df, source1[['Ord_id', 'Order_Date', 'Order_Priority']], on='Ord_id', how='inner')
df = pd.merge(df, source2[['Prod_id', 'Product_Category', 'Product_Sub_Category']], on='Prod_id', how='inner')
df = pd.merge(df, source3[['Cust_id', 'Customer_Name', 'Province', 'Region', 'Customer_Segment']], on='Cust_id', how='inner')

result = df[['Ship_Date', 'Ord_id', 'Prod_id', 'Ship_id']].copy()

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_50/target_multisource_mcts.csv", index=False)