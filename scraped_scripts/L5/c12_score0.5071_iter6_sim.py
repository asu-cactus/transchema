import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_4.csv", index_col=0)

pivot_result = source0.pivot(index='Ship_id', columns='Ship_Mode', values='Ship_id').reset_index()
# The pivoted columns contain Ship_Mode values as columns with Ship_id as values, but we only need Ship_Mode as a column in final output.
# Instead, we will keep Ship_Mode from source0 as is, so pivot is not useful here for final output.
# But as per partial plan, we do pivot first, then join.

# Actually, pivoting Ship_id by Ship_Mode with values Ship_id is redundant because Ship_id is unique per row.
# Instead, we can keep source0 as is for Ship_Mode and Ship_id.

# So we will follow the plan literally:
# pivot_result has Ship_id and columns for each Ship_Mode with Ship_id values or NaN.

# To get Ship_Mode per Ship_id, we can melt pivot_result back or just keep source0 as is.
# But to follow the plan, we keep pivot_result.

# Join source4 and source1 on Ord_id
join_1 = pd.merge(source4, source1, on='Ord_id', how='inner')

# Join join_1 with pivot_result on Ship_id
# pivot_result has Ship_id and columns for each Ship_Mode, but Ship_Mode is spread across columns.
# We need to get Ship_Mode back as a single column.

# To get Ship_Mode from pivot_result, melt it:
pivot_melt = pivot_result.melt(id_vars=['Ship_id'], var_name='Ship_Mode', value_name='Ship_id_val')
pivot_melt = pivot_melt[pivot_melt['Ship_id_val'].notna()].drop(columns=['Ship_id_val'])

# Now join join_1 with pivot_melt on Ship_id
join_2 = pd.merge(join_1, pivot_melt, on='Ship_id', how='inner')

# Join join_2 with source2 on Cust_id
join_3 = pd.merge(join_2, source2, on='Cust_id', how='inner')

# Join join_3 with source3 on Prod_id
join_4 = pd.merge(join_3, source3, on='Prod_id', how='inner')

# Select and reorder columns as per target schema
result = join_4[['Order_Priority', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

# Convert data types to match target schema
result['Order_Priority'] = result['Order_Priority'].astype(str)
result['Ship_Mode'] = result['Ship_Mode'].astype(str)
result['Ord_id'] = result['Ord_id'].astype(str)
result['Prod_id'] = result['Prod_id'].astype(str)
result['Ship_id'] = result['Ship_id'].astype(str)
result['Cust_id'] = result['Cust_id'].astype(str)
result['Sales'] = pd.to_numeric(result['Sales'], errors='coerce').fillna(0).astype(int)
result['Discount'] = pd.to_numeric(result['Discount'], errors='coerce').fillna(0).astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_12/target_multisource_mcts.csv", index=False)