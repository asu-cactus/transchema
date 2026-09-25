import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_80/training_0.csv", index_col=0)

df0['Purchase ID'] = pd.to_numeric(df0['Purchase ID'], errors='coerce').astype('Int64')
df0['SN'] = pd.to_numeric(df0['SN'], errors='coerce').astype('Int64', errors='ignore')  # SN looks like string, keep as is
df0['Age'] = pd.to_numeric(df0['Age'], errors='coerce').astype('Int64')
df0['Gender'] = pd.to_numeric(df0['Gender'], errors='coerce').astype('Int64')
df0['Item ID'] = pd.to_numeric(df0['Item ID'], errors='coerce').astype('Int64')
df0['Price'] = pd.to_numeric(df0['Price'], errors='coerce')

grouped = df0.groupby(['Item Name', 'Purchase ID', 'SN', 'Age', 'Gender', 'Item ID'], dropna=False).agg(
    Count_Price=('Price', 'count'),
    Min_Price=('Price', 'min'),
    Max_Price=('Price', 'max')
).reset_index()

# The target schema is:
# ['Item Name': string, 'Purchase ID': integer, 'SN': integer, 'Age': integer, 'Gender': integer, 'Item ID': integer,
#  'Price_x': integer, 'Purchase ID_x': integer, 'Age_x': integer, 'Item ID_x': integer,
#  'Price_y': float, 'Item ID_y': integer, 'Purchase ID_y': integer, 'Age_y': integer]

# The grouped table has columns:
# ['Item Name', 'Purchase ID', 'SN', 'Age', 'Gender', 'Item ID', 'Count_Price', 'Min_Price', 'Max_Price']

# We need to produce the target columns by joining the grouped table with itself or with the original table to get the multiple suffixed columns.

# From the target examples, it looks like the target table contains multiple sets of columns with suffixes _x and _y for Price, Purchase ID, Age, Item ID.

# Hypothesis: The target table is a join of the grouped aggregation with the original table or with itself on some keys.

# Let's try to join the grouped table with the original table on 'Item Name' and 'Purchase ID' and 'SN' and 'Age' and 'Gender' and 'Item ID' to get the _x and _y suffixed columns.

# But the target columns show Price_x as integer, Price_y as float, so maybe Price_x corresponds to Count_Price (integer), Price_y corresponds to Min_Price or Max_Price (float).

# Let's create a DataFrame with the grouped columns renamed to _x and _y suffixes accordingly.

# We'll create two DataFrames from grouped:
# One with Count_Price as Price_x and Purchase ID, Age, Item ID as _x suffix
# Another with Min_Price as Price_y and Purchase ID, Age as _y suffix

df_x = grouped.rename(columns={
    'Count_Price': 'Price_x',
    'Purchase ID': 'Purchase ID_x',
    'Age': 'Age_x',
    'Item ID': 'Item ID_x'
})[['Item Name', 'Purchase ID_x', 'SN', 'Age_x', 'Gender', 'Item ID_x', 'Price_x']]

df_y = grouped.rename(columns={
    'Min_Price': 'Price_y',
    'Purchase ID': 'Purchase ID_y',
    'Age': 'Age_y',
    'Item ID': 'Item ID_y'
})[['Item Name', 'Purchase ID_y', 'Age_y', 'Item ID_y', 'Price_y']]

# Now join df_x and df_y on 'Item Name' and 'Purchase ID' and 'Age' and 'Item ID'
# SN and Gender only appear in df_x, so keep them from df_x

merged = pd.merge(df_x, df_y, left_on=['Item Name', 'Purchase ID_x', 'Age_x', 'Item ID_x'],
                  right_on=['Item Name', 'Purchase ID_y', 'Age_y', 'Item ID_y'], how='inner')

# Reorder columns to match target schema
result = merged[['Item Name', 'Purchase ID_x', 'SN', 'Age_x', 'Gender', 'Item ID_x',
                 'Price_x', 'Purchase ID_x', 'Age_x', 'Item ID_x',
                 'Price_y', 'Item ID_y', 'Purchase ID_y', 'Age_y']]

# Rename columns to exact target schema names
result.columns = ['Item Name', 'Purchase ID', 'SN', 'Age', 'Gender', 'Item ID',
                  'Price_x', 'Purchase ID_x', 'Age_x', 'Item ID_x',
                  'Price_y', 'Item ID_y', 'Purchase ID_y', 'Age_y']

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_80/target_multisource_mcts.csv", index=False)