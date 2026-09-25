import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_78/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_78/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_78/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_78/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_78/training_4.csv", index_col=0)

# Join src3 with src2 on Ord_id
df = pd.merge(src3, src2, on='Ord_id', how='inner')

# Join with src1 on Ship_id
df = pd.merge(df, src1, on='Ship_id', how='inner')

# Join with src0 on Cust_id
df = pd.merge(df, src0, on='Cust_id', how='inner')

# Join with src4 on Prod_id
df = pd.merge(df, src4, on='Prod_id', how='inner')

# Group by Customer_Segment and Product_Category, aggregate sum of Profit
agg_df = df.groupby(['Customer_Segment', 'Product_Category'], as_index=False)['Profit'].sum()

# Project only Profit column to match target schema
result = agg_df[['Profit']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_78/target_multisource_mcts.csv", index=False)