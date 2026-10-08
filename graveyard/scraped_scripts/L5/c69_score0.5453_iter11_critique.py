import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_4.csv", index_col=0)

# Join Source5_69_3 and Source5_69_4 on Ship_id
join_34 = pd.merge(src3, src4, how='inner', on='Ship_id')

# Join with Source5_69_1 on Ord_id
join_341 = pd.merge(join_34, src1, how='inner', on='Ord_id')

# Join with Source5_69_2 on Cust_id
join_3412 = pd.merge(join_341, src2, how='inner', on='Cust_id')

# Join with Source5_69_0 on Prod_id (to use all source tables)
join_all = pd.merge(join_3412, src0, how='inner', on='Prod_id')

# Select only the target columns
result = join_all[['Ship_Date', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']]

# Remove duplicates if any
result = result.drop_duplicates(subset=['Ship_Date', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id'])

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_69/target_multisource_mcts.csv", index=False)