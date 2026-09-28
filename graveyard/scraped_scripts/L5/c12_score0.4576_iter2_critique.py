import pandas as pd

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_2.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_4.csv", index_col=0)

# Join source4 with source2 on Cust_id
join_1 = pd.merge(source4, source2, how='inner', left_on='Cust_id', right_on='Cust_id')

# Join with source1 on Ord_id
join_2 = pd.merge(join_1, source1, how='inner', left_on='Ord_id', right_on='Ord_id')

# Join with source0 on Ship_id
join_3 = pd.merge(join_2, source0, how='inner', left_on='Ship_id', right_on='Ship_id')

# Extract numeric part of IDs for Ord_id, Prod_id, Ship_id, Cust_id
# IDs are like "Ord_1082", "Prod_8", "SHP_1495", "Cust_417"
join_3['Ord_id'] = join_3['Ord_id'].str.extract(r'(\d+)').astype(int)
join_3['Prod_id'] = join_3['Prod_id'].str.extract(r'(\d+)').astype(int)
join_3['Ship_id'] = join_3['Ship_id'].str.extract(r'(\d+)').astype(int)
join_3['Cust_id'] = join_3['Cust_id'].str.extract(r'(\d+)').astype(int)

# Group by the leftmost columns (keys) and aggregate Sales and Discount by sum
result = join_3.groupby(
    ['Order_Priority', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id'],
    as_index=False
).agg({
    'Sales': 'sum',
    'Discount': 'sum'
})

# Convert Sales and Discount to int (they may be float after sum)
result['Sales'] = result['Sales'].round().astype(int)
result['Discount'] = result['Discount'].round().astype(int)

# Ensure Order_Priority and Ship_Mode are string
result['Order_Priority'] = result['Order_Priority'].astype(str)
result['Ship_Mode'] = result['Ship_Mode'].astype(str)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_12/target_multisource_mcts.csv", index=False)