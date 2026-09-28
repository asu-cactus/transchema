import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_81/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_81/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_81/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_81/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_81/training_4.csv", index_col=0)

# Join Source5_81_4 with Source5_81_1 on Ord_id
result = pd.merge(src4, src1, on='Ord_id', how='inner')

# Join with Source5_81_0 on Prod_id
result = pd.merge(result, src0, on='Prod_id', how='inner')

# Join with Source5_81_3 on Ship_id
result = pd.merge(result, src3, on='Ship_id', how='inner')

# Join with Source5_81_2 on Cust_id
result = pd.merge(result, src2, on='Cust_id', how='inner')

# Aggregate sum of Sales (no group by)
total_sales = result['Sales'].sum()

# Create final DataFrame with the same schema as target
final_df = pd.DataFrame({'Sales': [total_sales]})

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_81/target_multisource_mcts.csv", index=False)