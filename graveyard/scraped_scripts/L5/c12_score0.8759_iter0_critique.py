import pandas as pd

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_4.csv", index_col=0)

# Join all tables on keys
join1 = pd.merge(source4, source1, how='inner', left_on='Ord_id', right_on='Ord_id')
join2 = pd.merge(join1, source0, how='inner', left_on='Ship_id', right_on='Ship_id')
join3 = pd.merge(join2, source2, how='inner', left_on='Cust_id', right_on='Cust_id')
join4 = pd.merge(join3, source3, how='inner', left_on='Prod_id', right_on='Prod_id')

# Group by Order_Priority and Ship_Mode
grouped = join4.groupby(['Order_Priority', 'Ship_Mode'], as_index=False).agg({
    'Ord_id': pd.Series.nunique,
    'Prod_id': pd.Series.nunique,
    'Ship_id': pd.Series.nunique,
    'Cust_id': pd.Series.nunique,
    'Sales': 'sum',
    'Discount': 'sum'
})

# Rename columns to match target schema exactly
grouped.rename(columns={
    'Ord_id': 'Ord_id',
    'Prod_id': 'Prod_id',
    'Ship_id': 'Ship_id',
    'Cust_id': 'Cust_id',
    'Sales': 'Sales',
    'Discount': 'Discount'
}, inplace=True)

# The target schema expects integer types for IDs and numeric columns
# Convert counts and sums to integers (round sums if needed)
grouped['Ord_id'] = grouped['Ord_id'].astype(int)
grouped['Prod_id'] = grouped['Prod_id'].astype(int)
grouped['Ship_id'] = grouped['Ship_id'].astype(int)
grouped['Cust_id'] = grouped['Cust_id'].astype(int)
grouped['Sales'] = grouped['Sales'].round().astype(int)
grouped['Discount'] = grouped['Discount'].round().astype(int)

# Reorder columns to match target schema
result = grouped[['Order_Priority', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_12/target_multisource_mcts.csv", index=False)