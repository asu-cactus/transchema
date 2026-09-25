import pandas as pd

# Read all sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_81/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_81/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_81/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_81/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_81/training_4.csv", index_col=0)

# Join source4 with source0 on Prod_id
df = pd.merge(source4, source0, on='Prod_id', how='inner')

# Join with source1 on Ord_id
df = pd.merge(df, source1, on='Ord_id', how='inner')

# Join with source2 on Cust_id
df = pd.merge(df, source2, on='Cust_id', how='inner')

# Join with source3 on Ship_id
df = pd.merge(df, source3, on='Ship_id', how='inner')

# Group by the dimension columns and aggregate sum of Sales
group_cols = ['Product_Category', 'Order_Priority', 'Region', 'Ship_Mode']
result = df.groupby(group_cols, dropna=False, as_index=False)['Sales'].sum()

# Output only the Sales column as per target schema
result = result[['Sales']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_81/target_multisource_mcts.csv", index=False)