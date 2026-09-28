import pandas as pd
import re

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_4.csv", index_col=0)

# Join Source0 and Source4 on Ord_id
join_0_4 = pd.merge(source0, source4[['Ord_id', 'Order_Priority']], on='Ord_id', how='inner')

# Join with Source2 on Ship_id
join_0_4_2 = pd.merge(join_0_4, source2[['Ship_id', 'Ship_Mode']], on='Ship_id', how='inner')

# Join with Source1 on Cust_id
join_0_4_2_1 = pd.merge(join_0_4_2, source1[['Cust_id']], on='Cust_id', how='inner')

# Join with Source3 on Prod_id
full_join = pd.merge(join_0_4_2_1, source3[['Prod_id']], on='Prod_id', how='inner')

# Select relevant columns
df = full_join[['Order_Priority', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

# Extract numeric part of IDs and convert to int
def extract_int(s):
    # Extract digits from string like "Ord_1082" -> 1082
    return int(re.search(r'\d+', s).group())

df['Ord_id'] = df['Ord_id'].map(extract_int)
df['Prod_id'] = df['Prod_id'].map(extract_int)
df['Ship_id'] = df['Ship_id'].map(extract_int)
df['Cust_id'] = df['Cust_id'].map(extract_int)

# Aggregate: group by leftmost columns, sum Sales and Discount
agg_df = df.groupby(['Order_Priority', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id'], as_index=False).agg({
    'Sales': 'sum',
    'Discount': 'sum'
})

# Round Sales and convert to integer type
agg_df['Sales'] = agg_df['Sales'].round().astype('Int64')

# Discount is fraction, convert to percentage integer
agg_df['Discount'] = (agg_df['Discount'] * 100).round().astype('Int64')

# Reorder columns to match target schema exactly
agg_df = agg_df[['Order_Priority', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_71/target_multisource_mcts.csv", index=False)