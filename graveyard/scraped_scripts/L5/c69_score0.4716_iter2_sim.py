import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_4.csv", index_col=0)

# UNPIVOT step: The only source that contains the four key IDs together is s3.
# The target schema requires Ship_Date, which is in s4.
# The partial plan suggests unpivot first, but here unpivot is likely to reshape s3's multiple columns into rows.
# However, s3 already has the keys in columns, so unpivot likely means no operation here or a no-op.
# Given the partial plan, we interpret UNPIVOT as no change needed on s3, so we rename it as unpivot_result.
unpivot_result = s3.copy()

# Join unpivot_result with s1 on Ord_id to get Order_Date (to be renamed Ship_Date)
join_result_1 = pd.merge(unpivot_result, s1[['Ord_id', 'Order_Date']], on='Ord_id', how='left')

# Join with s4 on Ship_id to get Ship_Date (Ship_Date is in s4, but s1 also has Order_Date)
# Target Ship_Date is from s4 (Ship_Date), so we use s4's Ship_Date, not s1's Order_Date.
join_result_2 = pd.merge(join_result_1, s4[['Ship_id', 'Ship_Date']], on='Ship_id', how='left')

# The target schema is ['Ship_Date': string, 'Ord_id': integer, 'Prod_id': integer, 'Ship_id': integer, 'Cust_id': integer]
# Current IDs are strings like 'Ord_1', 'Prod_1', 'SHP_1', 'Cust_1'
# We need to convert these to integers by extracting the numeric part.

def extract_int_id(s):
    if pd.isna(s):
        return pd.NA
    return int(''.join(filter(str.isdigit, str(s))))

df = join_result_2.copy()
df['Ord_id'] = df['Ord_id'].map(extract_int_id)
df['Prod_id'] = df['Prod_id'].map(extract_int_id)
df['Ship_id'] = df['Ship_id'].map(extract_int_id)
df['Cust_id'] = df['Cust_id'].map(extract_int_id)

# Ship_Date is already string in format 'dd-mm-yyyy', keep as is.

# Select and reorder columns as target schema
df_target = df[['Ship_Date', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']]

df_target.to_csv("autopipeline-benchmarks/github-pipelines/length5_69/target_multisource_mcts.csv", index=False)