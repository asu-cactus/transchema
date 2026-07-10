import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_4.csv", index_col=0)

# Join s0 with s1 on Prod_id to get Product_Category
df = s0.merge(s1[['Prod_id', 'Product_Category']], on='Prod_id', how='inner')

# Join s0 with s2 on Ship_id (to use source 2)
df = df.merge(s2[['Ship_id']], on='Ship_id', how='inner')

# Join s0 with s3 on Cust_id (to use source 3)
df = df.merge(s3[['Cust_id']], on='Cust_id', how='inner')

# Join s0 with s4 on Ord_id (to use source 4)
df = df.merge(s4[['Ord_id']], on='Ord_id', how='inner')

# Convert Ord_id, Prod_id, Cust_id from strings like 'Ord_1082' to integers 1082
def extract_int(x):
    if pd.isna(x):
        return pd.NA
    return int(''.join(filter(str.isdigit, str(x))))

df['Ord_id'] = df['Ord_id'].apply(extract_int)
df['Prod_id'] = df['Prod_id'].apply(extract_int)
df['Cust_id'] = df['Cust_id'].apply(extract_int)

# Convert Sales to integer by rounding
df['Sales'] = df['Sales'].round().astype('Int64')

# Select columns as per target schema
result = df[['Product_Category', 'Ship_id', 'Ord_id', 'Prod_id', 'Cust_id', 'Sales']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_35/target_multisource_mcts.csv", index=False)