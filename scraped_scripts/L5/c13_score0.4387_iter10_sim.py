import pandas as pd
import re

def extract_int(s, prefix):
    if pd.isna(s):
        return None
    m = re.match(rf'{prefix}_(\d+)', s)
    return int(m.group(1)) if m else None

def discount_to_int(d):
    if pd.isna(d):
        return None
    return int(round(d * 100))

def sales_to_int(s):
    if pd.isna(s):
        return None
    return int(round(s))

src0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length5_13/training_0.csv', index_col=0)
src1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length5_13/training_1.csv', index_col=0)
src2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length5_13/training_2.csv', index_col=0)
src3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length5_13/training_3.csv', index_col=0)
src4 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length5_13/training_4.csv', index_col=0)

j1 = pd.merge(src1, src2, on='Cust_id', how='inner')
j2 = pd.merge(j1, src3, on='Prod_id', how='inner')
j3 = pd.merge(j2, src4, on='Ship_id', how='inner')
j4 = pd.merge(j3, src0, on='Ord_id', how='inner')

df = j4[['Product_Sub_Category', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']].copy()

df['Product_Sub_Category'] = df['Product_Sub_Category'].astype(str)
df['Ord_id'] = df['Ord_id'].map(lambda x: extract_int(x, 'Ord'))
df['Prod_id'] = df['Prod_id'].map(lambda x: extract_int(x, 'Prod'))
df['Ship_id'] = df['Ship_id'].map(lambda x: extract_int(x, 'SHP'))
df['Cust_id'] = df['Cust_id'].map(lambda x: extract_int(x, 'Cust'))
df['Sales'] = df['Sales'].map(sales_to_int)
df['Discount'] = df['Discount'].map(discount_to_int)

df.to_csv('autopipeline-benchmarks/github-pipelines/length5_13/target_multisource_mcts.csv', index=False)