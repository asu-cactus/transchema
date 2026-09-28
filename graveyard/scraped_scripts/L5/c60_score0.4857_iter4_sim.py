import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_60/training_0.csv", index_col=0)

df = df0.copy()

# UNPIVOT step: The partial plan suggests unpivoting on SN, Age, Gender, Item ID, Item Name, Price
# But these columns are already in a normalized form (no wide columns to unpivot).
# So we interpret UNPIVOT as reshaping if there were multiple purchase counts or IDs per row.
# Since source has Purchase ID, SN, Age, Gender, Item ID, Item Name, Price, and target has many columns with suffixes,
# we need to create multiple "purchase" related columns by grouping or aggregating.

# The target schema has multiple columns with suffixes _x and _y and also base columns.
# This suggests the target is a join or aggregation of multiple purchase records per SN or similar.

# Since only one source table is given, and no other source tables,
# we interpret the partial plan as grouping by SN, Age, Gender, Item ID, Item Name, Price,
# and aggregating counts and averages to produce the target columns.

# We will create:
# Purchase Count: count of purchases per group
# Purchase ID_x: average Purchase ID (float)
# Age_x: min Age (int)
# Age_y: max Age (int)
# Item ID_x: min Item ID (int)
# Item ID_y: max Item ID (float)
# Average Purchase Price: average Price (float)
# Purchase ID_y: max Purchase ID (int)
# Age: sum Age (int)
# Item ID: sum Item ID (int)
# Total Purchase Value: sum Price * Purchase Count or sum Price

# Because target columns have _x and _y suffixes, we simulate two aggregations per group.

group_cols = ['SN', 'Age', 'Gender', 'Item ID', 'Item Name', 'Price']

agg_df = df.groupby(group_cols).agg(
    Purchase_Count=('Purchase ID', 'count'),
    Purchase_ID_x=('Purchase ID', 'mean'),
    Age_x=('Age', 'min'),
    Age_y=('Age', 'max'),
    Item_ID_x=('Item ID', 'min'),
    Item_ID_y=('Item ID', 'max'),
    Average_Purchase_Price=('Price', 'mean'),
    Purchase_ID_y=('Purchase ID', 'max'),
    Age_sum=('Age', 'sum'),
    Item_ID_sum=('Item ID', 'sum'),
    Total_Purchase_Value=('Price', 'sum')
).reset_index()

# Rename columns to match target schema exactly
agg_df.rename(columns={
    'Purchase_Count': 'Purchase Count',
    'SN': 'SN',
    'Age_x': 'Age_x',
    'Gender': 'Gender',
    'Item_ID_x': 'Item ID_x',
    'Item Name': 'Item Name',
    'Price': 'Price',
    'Purchase_ID_x': 'Purchase ID_x',
    'Age_y': 'Age_y',
    'Item_ID_y': 'Item ID_y',
    'Average_Purchase_Price': 'Average Purchase Price',
    'Purchase_ID_y': 'Purchase ID_y',
    'Age_sum': 'Age',
    'Item_ID_sum': 'Item ID',
    'Total_Purchase_Value': 'Total Purchase Value'
}, inplace=True)

# Convert types to match target schema
agg_df['Purchase Count'] = agg_df['Purchase Count'].astype(int)
agg_df['SN'] = agg_df['SN'].astype(str)
agg_df['Age_x'] = agg_df['Age_x'].astype(int)
agg_df['Gender'] = agg_df['Gender'].astype(str)
agg_df['Item ID_x'] = agg_df['Item ID_x'].astype(int)
agg_df['Item Name'] = agg_df['Item Name'].astype(str)
agg_df['Price'] = agg_df['Price'].astype(float)
agg_df['Purchase ID_x'] = agg_df['Purchase ID_x'].astype(float)
agg_df['Age_y'] = agg_df['Age_y'].astype(int)
agg_df['Item ID_y'] = agg_df['Item ID_y'].astype(float)
agg_df['Average Purchase Price'] = agg_df['Average Purchase Price'].astype(float)
agg_df['Purchase ID_y'] = agg_df['Purchase ID_y'].astype(int)
agg_df['Age'] = agg_df['Age'].astype(int)
agg_df['Item ID'] = agg_df['Item ID'].astype(int)
agg_df['Total Purchase Value'] = agg_df['Total Purchase Value'].astype(float)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_60/target_multisource_mcts.csv", index=False)