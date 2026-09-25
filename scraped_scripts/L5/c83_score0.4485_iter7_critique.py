import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_4.csv", index_col=0)

# Join Source5_83_4 and Source5_83_1 on Ord_id
merged = pd.merge(src4, src1, how='inner', left_on='Ord_id', right_on='Ord_id')

# Join with Source5_83_2 on Ship_id
merged = pd.merge(merged, src2, how='inner', left_on='Ship_id', right_on='Ship_id')

# Join with Source5_83_0 on Cust_id
merged = pd.merge(merged, src0, how='inner', left_on='Cust_id', right_on='Cust_id')

# Join with Source5_83_3 on Prod_id
merged = pd.merge(merged, src3, how='inner', left_on='Prod_id', right_on='Prod_id')

# Group by Customer_Segment and Order_Priority, aggregate sum of Profit
agg = merged.groupby(['Customer_Segment', 'Order_Priority'], as_index=False).agg({'Profit': 'sum'})

# Select only Profit column to match target schema
result = agg[['Profit']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_83/target_multisource_mcts.csv", index=False)