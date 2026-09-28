import pandas as pd

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_4.csv", index_col=0)

# Join df4 with df0 on Prod_id to get Product_Sub_Category
join1 = pd.merge(df4, df0[['Product_Sub_Category', 'Prod_id']], how='inner', left_on='Prod_id', right_on='Prod_id')

# Join with df1 on Cust_id
join2 = pd.merge(join1, df1[['Cust_id']], how='inner', left_on='Cust_id', right_on='Cust_id')

# Join with df3 on Ship_id
join3 = pd.merge(join2, df3[['Ship_id']], how='inner', left_on='Ship_id', right_on='Ship_id')

# Join with df2 on Ord_id
join4 = pd.merge(join3, df2[['Ord_id']], how='inner', left_on='Ord_id', right_on='Ord_id')

# Group by the leftmost columns of the target schema (keys)
group_cols = ['Product_Sub_Category', 'Order_Quantity', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']

agg_df = join4.groupby(group_cols, as_index=False).agg({
    'Sales': 'sum',
    'Discount': 'sum'
})

# Convert columns to required types and formats

# Convert IDs from string like 'Ord_1082' to integer 1082
agg_df['Ord_id'] = agg_df['Ord_id'].apply(lambda x: int(x.split('_')[1]) if isinstance(x, str) and '_' in x else x)
agg_df['Prod_id'] = agg_df['Prod_id'].apply(lambda x: int(x.split('_')[1]) if isinstance(x, str) and '_' in x else x)
agg_df['Ship_id'] = agg_df['Ship_id'].apply(lambda x: int(x.split('_')[1]) if isinstance(x, str) and '_' in x else x)
agg_df['Cust_id'] = agg_df['Cust_id'].apply(lambda x: int(x.split('_')[1]) if isinstance(x, str) and '_' in x else x)

# Order_Quantity is integer already, but ensure type
agg_df['Order_Quantity'] = agg_df['Order_Quantity'].astype(int)

# Round Sales and convert to int
agg_df['Sales'] = agg_df['Sales'].round().astype(int)

# Discount is a fraction, multiply by 100 and round to int
agg_df['Discount'] = (agg_df['Discount'] * 100).round().astype(int)

# Reorder columns to match target schema exactly
agg_df = agg_df[['Product_Sub_Category', 'Order_Quantity', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_7/target_multisource_mcts.csv", index=False)