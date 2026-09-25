import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_4.csv", index_col=0)

# UNPIVOT operation on df1 for Order_Quantity (though df1 already has Order_Quantity as a column, 
# the partial plan suggests unpivot, but since no multiple quantity columns exist, we keep as is)
# So no actual unpivot needed, just rename for clarity
unpivot_df = df1[['Order_Quantity', 'Ship_id', 'Ord_id', 'Prod_id', 'Cust_id', 'Sales']].copy()

# Join unpivot_df with df4 on Ship_id to get Ship_Mode
join1 = pd.merge(unpivot_df, df4[['Ship_Mode', 'Ship_id']], on='Ship_id', how='left')

# The target schema is:
# ['Order_Quantity': integer, 'Ship_Mode': string, 'Ord_id': integer, 'Prod_id': integer, 'Ship_id': integer, 'Cust_id': integer, 'Sales': integer]
# We need to convert IDs like Ord_id, Prod_id, Ship_id, Cust_id from strings like 'Ord_1082' to integers 1082 etc.

def extract_int_id(s):
    if pd.isna(s):
        return pd.NA
    import re
    m = re.search(r'(\d+)', s)
    return int(m.group(1)) if m else pd.NA

join1['Ord_id'] = join1['Ord_id'].map(extract_int_id)
join1['Prod_id'] = join1['Prod_id'].map(extract_int_id)
join1['Ship_id'] = join1['Ship_id'].map(extract_int_id)
join1['Cust_id'] = join1['Cust_id'].map(extract_int_id)

# Convert Sales and Order_Quantity to integer (Sales might be float, but target expects integer)
join1['Sales'] = join1['Sales'].round().astype('Int64')
join1['Order_Quantity'] = join1['Order_Quantity'].astype('Int64')

# Reorder columns to target schema
result = join1[['Order_Quantity', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_18/target_multisource_mcts.csv", index=False)