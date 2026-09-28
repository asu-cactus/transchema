import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_4.csv", index_col=0)

# Join Source4 with Source1 on Ord_id
result = pd.merge(df4, df1, how='inner', on='Ord_id')

# Join with Source2 on Ship_id
result = pd.merge(result, df2, how='inner', on='Ship_id')

# Join with Source0 on Cust_id
result = pd.merge(result, df0, how='inner', on='Cust_id')

# Join with Source3 on Prod_id
result = pd.merge(result, df3, how='inner', on='Prod_id')

# Aggregate sum of Profit (no group by)
result = pd.DataFrame({'Profit': [result['Profit'].sum()]})

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_83/target_multisource_mcts.csv", index=False)