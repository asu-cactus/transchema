import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_78/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_78/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_78/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_78/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_78/training_4.csv", index_col=0)

# Join Source3 and Source1 on Ship_id
joined = pd.merge(source3, source1, how='inner', on='Ship_id')

# Join with Source2 on Ord_id
joined = pd.merge(joined, source2, how='inner', on='Ord_id')

# Join with Source0 on Cust_id
joined = pd.merge(joined, source0, how='inner', on='Cust_id')

# Join with Source4 on Prod_id
joined = pd.merge(joined, source4, how='inner', on='Prod_id')

# Group by Province and Customer_Segment, aggregate sum of Profit
result = joined.groupby(['Province', 'Customer_Segment'], as_index=False)['Profit'].sum()

# Keep only Profit column as per target schema
result = result[['Profit']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_78/target_multisource_mcts.csv", index=False)