import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_94/training_1.csv", index_col=0)

grouped = df0.groupby(['Date', 'IsHoliday'], dropna=False).agg(
    Weekly_Sales_sum=pd.NamedAgg(column='Weekly_Sales', aggfunc='sum'),
    Store_count=pd.NamedAgg(column='Store', aggfunc='count'),
    Dept_count=pd.NamedAgg(column='Dept', aggfunc='count')
).reset_index()

grouped = grouped.rename(columns={
    'Weekly_Sales_sum': 'Weekly_Sales',
    'Store_count': 'Store',
    'Dept_count': 'Dept'
})

grouped['Store'] = grouped['Store'].astype(float)
grouped['Dept'] = grouped['Dept'].astype(float)
grouped['Date'] = grouped['Date'].astype(str)
grouped['IsHoliday'] = grouped['IsHoliday'].astype(str)

# The partial plan suggests using ID as join key, but grouped does not have ID.
# We need to create an ID column in grouped to join with df1 on ID.
# However, df0 has no ID column, so we cannot join on ID directly.
# The target schema requires ID, shop_id, item_id from df1.
# The only way to join is to add an ID column to grouped matching df1.ID.
# But grouped has no ID column, so we cannot join on ID.
# The prompt's partial plan is ambiguous about how to get ID in grouped.
# Since df0 has no ID, and df1 has only ID, shop_id, item_id, the only way is to join on Date and IsHoliday? No.
# The target examples show Store, Dept, Date, Weekly_Sales, IsHoliday, ID, shop_id, item_id.
# So the best guess is to join df1 to grouped on ID, but grouped has no ID.
# Possibly the COUNT(Store) and COUNT(Dept) are used as Store and Dept, but ID is from df1.
# So we must create a synthetic ID in grouped to join with df1.
# But no such ID exists.
# The only way is to join df1 to grouped without keys, i.e., cross join, which is not correct.
# Alternatively, the prompt's partial plan is incomplete or incorrect.
# Given the target schema and source schemas, the best approach is to join df1 to df0 on no keys, but that is not possible.
# The only common column is Date and IsHoliday in df0, and ID in df1.
# So we must produce the target by concatenating columns from grouped and df1 side by side.
# The target examples show many NaNs in Store, Dept, Date, Weekly_Sales, IsHoliday when ID, shop_id, item_id are present.
# So the final target is a vertical union of grouped df0 aggregation and df1 data with NaNs for missing columns.
# So the plan is:
# 1) group df0 by Date and IsHoliday with aggregations, producing Store, Dept, Date, Weekly_Sales, IsHoliday columns, ID, shop_id, item_id as NaN
# 2) df1 with ID, shop_id, item_id columns, Store, Dept, Date, Weekly_Sales, IsHoliday as NaN
# 3) concat vertically both dataframes to produce final target.

# Implementing this plan:

grouped['ID'] = pd.NA
grouped['shop_id'] = pd.NA
grouped['item_id'] = pd.NA

df1['Store'] = pd.NA
df1['Dept'] = pd.NA
df1['Date'] = pd.NA
df1['Weekly_Sales'] = pd.NA
df1['IsHoliday'] = pd.NA

df1 = df1[['Store', 'Dept', 'Date', 'Weekly_Sales', 'IsHoliday', 'ID', 'shop_id', 'item_id']]
grouped = grouped[['Store', 'Dept', 'Date', 'Weekly_Sales', 'IsHoliday', 'ID', 'shop_id', 'item_id']]

result = pd.concat([grouped, df1], ignore_index=True)

result['Store'] = result['Store'].astype('float64')
result['Dept'] = result['Dept'].astype('float64')
result['Date'] = result['Date'].astype('string')
result['Weekly_Sales'] = result['Weekly_Sales'].astype('float64')
result['IsHoliday'] = result['IsHoliday'].astype('string')
result['ID'] = pd.to_numeric(result['ID'], errors='coerce')
result['shop_id'] = pd.to_numeric(result['shop_id'], errors='coerce')
result['item_id'] = pd.to_numeric(result['item_id'], errors='coerce')

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_94/target_multisource_mcts.csv", index=False)