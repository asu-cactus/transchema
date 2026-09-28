import pandas as pd

# Read source table twice with different aliases
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_80/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_80/training_0.csv", index_col=0)

# Rename columns in df0 and df1 to prepare for join with suffixes
df0_renamed = df0.rename(columns={
    'Price': 'Price_x',
    'Purchase ID': 'Purchase ID_x',
    'Age': 'Age_x',
    'Item ID': 'Item ID_x'
})

df1_renamed = df1.rename(columns={
    'Price': 'Price_y',
    'Purchase ID': 'Purchase ID_y',
    'Age': 'Age_y',
    'Item ID': 'Item ID_y'
})

# Join on Purchase ID (original column in df0 and df1)
# Since we renamed Purchase ID columns, join on original Purchase ID columns before renaming
# So join on df0['Purchase ID'] == df1['Purchase ID']
joined = pd.merge(df0_renamed, df1_renamed,
                  left_on='Purchase ID_x', right_on='Purchase ID_y',
                  suffixes=('_x', '_y'),
                  how='inner')

# The joined dataframe now has columns:
# Item Name_x, SN_x, Gender_x, Price_x, Purchase ID_x, Age_x, Item ID_x,
# Item Name_y, SN_y, Gender_y, Price_y, Purchase ID_y, Age_y, Item ID_y

# We want to keep Item Name from df0 (Item Name_x), Purchase ID from df0 (Purchase ID_x),
# SN from df0 (SN_x), Age from df0 (Age_x), Gender from df0 (Gender_x), Item ID from df0 (Item ID_x),
# Price_x from df0 (Price_x),
# Purchase ID_x, Age_x, Item ID_x (already from df0),
# Price_y from df1 (Price_y),
# Item ID_y, Purchase ID_y, Age_y from df1

# Convert SN_x and Gender_x to integer codes
joined['SN'] = joined['SN_x'].astype('category').cat.codes
joined['Gender'] = joined['Gender_x'].astype('category').cat.codes

# Convert Purchase ID_x, Age_x, Item ID_x to int
joined['Purchase ID'] = joined['Purchase ID_x'].astype(int)
joined['Age'] = joined['Age_x'].astype(int)
joined['Item ID'] = joined['Item ID_x'].astype(int)

# Convert Price_x to int (round or floor)
joined['Price_x'] = joined['Price_x'].round().astype(int)

# Price_y is float, keep as is
joined['Price_y'] = joined['Price_y'].astype(float)

# Convert Purchase ID_y, Age_y, Item ID_y to int
joined['Purchase ID_y'] = joined['Purchase ID_y'].astype(int)
joined['Age_y'] = joined['Age_y'].astype(int)
joined['Item ID_y'] = joined['Item ID_y'].astype(int)

# Item Name from df0 (Item Name_x)
joined['Item Name'] = joined['Item Name_x'].astype(str)

# Group by leftmost columns: Item Name, Purchase ID, SN
group_cols = ['Item Name', 'Purchase ID', 'SN']

# Aggregate Price_x and Price_y by sum (or mean if needed)
agg_df = joined.groupby(group_cols, as_index=False).agg({
    'Age': 'first',  # Age is same per Purchase ID, so first is fine
    'Gender': 'first',  # same for Gender
    'Item ID': 'first',
    'Price_x': 'sum',
    'Purchase ID_x': 'first',
    'Age_x': 'first',
    'Item ID_x': 'first',
    'Price_y': 'sum',
    'Item ID_y': 'first',
    'Purchase ID_y': 'first',
    'Age_y': 'first'
})

# Reorder columns to match target schema exactly
target_cols = ['Item Name', 'Purchase ID', 'SN', 'Age', 'Gender', 'Item ID',
               'Price_x', 'Purchase ID_x', 'Age_x', 'Item ID_x',
               'Price_y', 'Item ID_y', 'Purchase ID_y', 'Age_y']

target_df = agg_df[target_cols]

# Write to CSV
target_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_80/target_multisource_mcts.csv", index=False)