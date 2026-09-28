import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_85/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_85/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_85/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_85/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_85/training_4.csv", index_col=0)

join_1 = pd.merge(source4, source2, how='inner', left_on='Cust_id', right_on='Cust_id')
join_2 = pd.merge(join_1, source3, how='inner', left_on='Prod_id', right_on='Prod_id')
join_3 = pd.merge(join_2, source0, how='inner', left_on='Ship_id', right_on='Ship_id')
join_4 = pd.merge(join_3, source1, how='inner', left_on='Ord_id', right_on='Ord_id')

# Group by Product_Category and Customer_Segment, aggregate sum of Sales
target = join_4.groupby(['Product_Category', 'Customer_Segment'], as_index=False)['Sales'].sum()

# Keep only Sales column as in target schema
target = target[['Sales']]

target.to_csv("autopipeline-benchmarks/github-pipelines/length5_85/target_multisource_mcts.csv", index=False)