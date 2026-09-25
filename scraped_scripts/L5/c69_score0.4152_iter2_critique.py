import pandas as pd

# Read all sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_4.csv", index_col=0)

# Join s3 (fact) with s1 (orders) on Ord_id to get Order_Date (not used in final, but needed to use s1)
df = pd.merge(s3, s1[['Ord_id', 'Order_Date']], on='Ord_id', how='inner')

# Join with s4 (shipping) on Ship_id to get Ship_Date (needed for target)
df = pd.merge(df, s4[['Ship_id', 'Ship_Date']], on='Ship_id', how='inner')

# Join with s0 (product) on Prod_id to use Source5_69_0
df = pd.merge(df, s0[['Prod_id']], on='Prod_id', how='inner')

# Join with s2 (customer) on Cust_id to use Source5_69_2
df = pd.merge(df, s2[['Cust_id']], on='Cust_id', how='inner')

# Extract integer IDs from string IDs
def extract_int_id(s):
    if pd.isna(s):
        return pd.NA
    return int(''.join(filter(str.isdigit, str(s))))

df['Ord_id'] = df['Ord_id'].map(extract_int_id)
df['Prod_id'] = df['Prod_id'].map(extract_int_id)
df['Ship_id'] = df['Ship_id'].map(extract_int_id)
df['Cust_id'] = df['Cust_id'].map(extract_int_id)

# Ship_Date is already string in 'dd-mm-yyyy' format, keep as is

# Group by all target columns to remove duplicates and ensure uniqueness
df_grouped = df.groupby(['Ship_Date', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id'], as_index=False).agg({'Ord_id':'count'})

# Select only target columns (drop the aggregation count column)
df_target = df_grouped[['Ship_Date', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']]

# Write output
df_target.to_csv("autopipeline-benchmarks/github-pipelines/length5_69/target_multisource_mcts.csv", index=False)