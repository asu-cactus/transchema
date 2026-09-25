import pandas as pd

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

# Group by Ord_id and sum Sales
result = df.groupby('Ord_id', as_index=False).agg(Sales=('Sales', 'sum'))

# Output only Sales column
final = result[['Sales']].copy()

final.to_csv("autopipeline-benchmarks/github-pipelines/length5_81/target_multisource_mcts.csv", index=False)