import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_78/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_78/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_78/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_78/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_78/training_4.csv", index_col=0)

# Join source3 with source2 on Ord_id
df = pd.merge(source3, source2, on='Ord_id', how='inner')

# Join with source1 on Ship_id
df = pd.merge(df, source1, on='Ship_id', how='inner')

# Join with source0 on Cust_id
df = pd.merge(df, source0, on='Cust_id', how='inner')

# Join with source4 on Prod_id
df = pd.merge(df, source4, on='Prod_id', how='inner')

# Group by Product_Category and sum Profit
result = df.groupby('Product_Category', as_index=False)['Profit'].sum()

# Rename column to match target schema exactly (already 'Profit')
# The target schema has only one column 'Profit', so we output only that column
# But since the target examples have 4 rows, and grouping by Product_Category may produce more,
# we keep all groups as is (no filtering).

# Output only the Profit column as per target schema
# But target schema is ['Profit'], so output that column only
# The target examples show only Profit column, so drop Product_Category column
result = result[['Profit']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_78/target_multisource_mcts.csv", index=False)