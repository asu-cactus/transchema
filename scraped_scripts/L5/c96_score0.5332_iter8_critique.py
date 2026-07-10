import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_96/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_96/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_96/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_96/training_4.csv", index_col=0)

# Join df2 and df3 on 'Ord_id'
result = pd.merge(df2, df3, on='Ord_id', how='inner')

# Join with df1 on 'Ship_id'
result = pd.merge(result, df1, on='Ship_id', how='inner')

# Join with df0 on 'Cust_id'
result = pd.merge(result, df0, on='Cust_id', how='inner')

# Join with df4 on 'Prod_id'
result = pd.merge(result, df4, on='Prod_id', how='inner')

# Group by 'Region' and aggregate sum of 'Profit'
agg_result = result.groupby('Region', as_index=False)['Profit'].sum()

# Output only 'Profit' column as per target schema
agg_result = agg_result[['Profit']]

agg_result.to_csv("autopipeline-benchmarks/github-pipelines/length5_96/target_multisource_mcts.csv", index=False)