import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_87/training_4.csv", index_col=0)

# Join Source0 and Source4 on Order_ID
df = pd.merge(source0, source4, on='Order_ID', how='inner')

# Join with Source2 on Ord_id
df = pd.merge(df, source2, on='Ord_id', how='inner')

# Join with Source1 on Prod_id
df = pd.merge(df, source1, on='Prod_id', how='inner')

# Join with Source3 on Cust_id
df = pd.merge(df, source3, on='Cust_id', how='inner')

# Group by Order_ID and sum Profit
result = df.groupby('Order_ID', as_index=False)['Profit'].sum()

# Rename column to match target schema (Profit)
result = result[['Profit']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_87/target_multisource_mcts.csv", index=False)