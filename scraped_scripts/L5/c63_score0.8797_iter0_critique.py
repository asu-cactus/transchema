import pandas as pd

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_4.csv", index_col=0)

# Join all dimension tables to the fact table on their keys
df = source4.merge(source0[['Ord_id']], on='Ord_id', how='inner') \
            .merge(source1[['Cust_id']], on='Cust_id', how='inner') \
            .merge(source2[['Prod_id']], on='Prod_id', how='inner') \
            .merge(source3[['Ship_id']], on='Ship_id', how='inner')

# Define a helper function to convert string IDs like 'Ord_1082' to integer 1082
def id_to_int(x):
    if pd.isna(x):
        return x
    return int(x.split('_')[1])

# Convert ID columns to integers before aggregation for correct min
df['Ord_id_int'] = df['Ord_id'].map(id_to_int)
df['Ship_id_int'] = df['Ship_id'].map(id_to_int)
df['Cust_id_int'] = df['Cust_id'].map(id_to_int)

# Group by Prod_id and aggregate
grouped = df.groupby('Prod_id', as_index=False).agg({
    'Ord_id_int': 'min',
    'Ship_id_int': 'min',
    'Cust_id_int': 'min',
    'Sales': 'sum',
    'Discount': 'sum'
})

# Rename columns to match target schema
grouped = grouped.rename(columns={
    'Ord_id_int': 'Ord_id',
    'Ship_id_int': 'Ship_id',
    'Cust_id_int': 'Cust_id'
})

# Convert Sales and Discount to int, Discount multiplied by 100 to match target scale
grouped['Sales'] = grouped['Sales'].astype(int)
grouped['Discount'] = (grouped['Discount'] * 100).astype(int)

# Reorder columns as per target schema
result = grouped[['Prod_id', 'Ord_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_63/target_multisource_mcts.csv", index=False)