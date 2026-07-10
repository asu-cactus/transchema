import pandas as pd
import re

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_4.csv", index_col=0)

# Join df4 with df0 on Cust_id to get Customer_Name
join1 = pd.merge(df4, df0[['Customer_Name', 'Cust_id']], on='Cust_id', how='inner')

# Join with df2 on Ord_id
join2 = pd.merge(join1, df2[['Ord_id']], on='Ord_id', how='inner')

# Join with df3 on Prod_id
join3 = pd.merge(join2, df3[['Prod_id']], on='Prod_id', how='inner')

# Join with df1 on Ship_id (missing in original)
join4 = pd.merge(join3, df1[['Ship_id']], on='Ship_id', how='inner')

# Extract numeric part from Ord_id, Prod_id, Ship_id and convert to int
def extract_int(s):
    # Extract digits from string like 'Ord_1082' -> 1082
    return int(re.search(r'\d+', s).group())

join4['Ord_id'] = join4['Ord_id'].map(extract_int)
join4['Prod_id'] = join4['Prod_id'].map(extract_int)
join4['Ship_id'] = join4['Ship_id'].map(extract_int)

# Select target columns
result = join4[['Customer_Name', 'Ord_id', 'Prod_id', 'Ship_id']]

# Group by all key columns to remove duplicates (no aggregation needed)
result = result.drop_duplicates(subset=['Customer_Name', 'Ord_id', 'Prod_id', 'Ship_id'])

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_46/target_multisource_mcts.csv", index=False)