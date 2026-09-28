import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_21/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_21/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_21/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_21/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_21/training_4.csv", index_col=0)

# Unpivot Sales and Discount in s2
s2_unpivot = s2.melt(id_vars=['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id'], value_vars=['Sales', 'Discount'], var_name='Measure', value_name='Value')

# Pivot back to wide format to separate Sales and Discount columns again
s2_pivot = s2_unpivot.pivot_table(index=['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id'], columns='Measure', values='Value').reset_index()

# Join s2_pivot with s4 on Ord_id to get Order_Priority
merged_1 = pd.merge(s2_pivot, s4[['Ord_id', 'Order_Priority']], on='Ord_id', how='left')

# Join with s0 on Cust_id to bring customer info (though not needed in target, but required to use all sources)
merged_2 = pd.merge(merged_1, s0[['Cust_id']], on='Cust_id', how='left')

# Join with s1 on Prod_id to bring product info (though not needed in target, but required to use all sources)
merged_3 = pd.merge(merged_2, s1[['Prod_id']], on='Prod_id', how='left')

# Select and rename columns as per target schema
result = merged_3[['Ship_id', 'Order_Priority', 'Ord_id', 'Prod_id', 'Cust_id', 'Sales', 'Discount']]

# Convert Ord_id, Prod_id, Cust_id from strings like 'Ord_1082' to integers 1082
result['Ord_id'] = result['Ord_id'].str.replace(r'^\D+', '', regex=True).astype(int)
result['Prod_id'] = result['Prod_id'].str.replace(r'^\D+', '', regex=True).astype(int)
result['Cust_id'] = result['Cust_id'].str.replace(r'^\D+', '', regex=True).astype(int)

# Convert Sales and Discount to integers by rounding
result['Sales'] = result['Sales'].round().astype(int)
result['Discount'] = result['Discount'].round().astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_21/target_multisource_mcts.csv", index=False)