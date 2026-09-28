import pandas as pd

# Read all source tables
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_74/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_74/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_74/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_74/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_74/training_4.csv", index_col=0)

# Join Source5_74_4 with Source5_74_1 on Ord_id
result = pd.merge(source4, source1, on='Ord_id', how='inner')

# Join with Source5_74_0 on Prod_id
result = pd.merge(result, source0, on='Prod_id', how='inner')

# Join with Source5_74_3 on Ship_id
result = pd.merge(result, source3, on='Ship_id', how='inner')

# Join with Source5_74_2 on Cust_id
result = pd.merge(result, source2, on='Cust_id', how='inner')

# Group by Ord_id and sum Profit
result = result.groupby('Ord_id', as_index=False)['Profit'].sum()

# Keep only Profit column as per target schema
result = result[['Profit']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_74/target_multisource_mcts.csv", index=False)