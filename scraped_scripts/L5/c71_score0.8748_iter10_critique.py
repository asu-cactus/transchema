import pandas as pd

# Read all source tables
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_4.csv", index_col=0)

# Join Source0 with Source2 on Ship_id
join_0_2 = pd.merge(source0, source2, how='inner', on='Ship_id')

# Join with Source1 on Cust_id
join_0_2_1 = pd.merge(join_0_2, source1, how='inner', on='Cust_id')

# Join with Source4 on Ord_id
join_0_2_1_4 = pd.merge(join_0_2_1, source4, how='inner', on='Ord_id')

# Join with Source3 on Prod_id
join_all = pd.merge(join_0_2_1_4, source3, how='inner', on='Prod_id')

# Convert IDs from string to int by removing prefixes
for col, prefix in [('Ord_id', 'Ord_'), ('Prod_id', 'Prod_'), ('Ship_id', 'SHP_'), ('Cust_id', 'Cust_')]:
    join_all[col] = join_all[col].str.replace(prefix, '', regex=False).astype(int)

# Convert Sales to integer by rounding sum
# Convert Discount to integer percentage by summing and multiplying by 100
# Group by Order_Priority and Ship_Mode
grouped = join_all.groupby(['Order_Priority', 'Ship_Mode']).agg(
    Ord_id=pd.NamedAgg(column='Ord_id', aggfunc=lambda x: x.nunique()),
    Prod_id=pd.NamedAgg(column='Prod_id', aggfunc=lambda x: x.nunique()),
    Ship_id=pd.NamedAgg(column='Ship_id', aggfunc=lambda x: x.nunique()),
    Cust_id=pd.NamedAgg(column='Cust_id', aggfunc=lambda x: x.nunique()),
    Sales=pd.NamedAgg(column='Sales', aggfunc='sum'),
    Discount=pd.NamedAgg(column='Discount', aggfunc='sum')
).reset_index()

# Round Sales and Discount as integers
grouped['Sales'] = grouped['Sales'].round().astype(int)
grouped['Discount'] = (grouped['Discount'] * 100).round().astype(int)

# Reorder columns to match target schema exactly
result = grouped[['Order_Priority', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

# Write to CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_71/target_multisource_mcts.csv", index=False)