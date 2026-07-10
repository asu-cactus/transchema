import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_53/training_0.csv", index_col=0)

# Create Age Category as int from Age
df0['Age Category'] = df0['Age'].astype(int)

# Purchase ID as int
df0['Purchase ID'] = df0['Purchase ID'].astype(int)

# Factorize SN, Item Name, and Price (to int codes starting from 1)
df0['SN'] = pd.factorize(df0['SN'])[0] + 1
df0['Item Name'] = pd.factorize(df0['Item Name'])[0] + 1
df0['Price_code'] = pd.factorize(df0['Price'])[0] + 1  # factorized price for grouping

# Purchase Count = 1
df0['Purchase Count'] = 1

# Map Gender to int
df0['Gender'] = df0['Gender'].map({'Male':1, 'Female':2}).fillna(0).astype(int)

# Item ID as int
df0['Item ID'] = df0['Item ID'].astype(int)

# Keep original Price as float for aggregation
df0['Price'] = df0['Price'].astype(float)

# Group by the leftmost columns (including factorized Price_code)
grouped = df0.groupby([
    'Age Category', 'Purchase ID', 'SN', 'Purchase Count', 'Gender', 'Item ID', 'Item Name', 'Price_code'
]).agg(
    Total_Purchase_Value = ('Price', 'sum'),
    Average_Purchase_Price = ('Price', 'mean')
).reset_index()

# Rename Price_code back to Price (int)
grouped = grouped.rename(columns={'Price_code': 'Price'})

# Cast columns to correct types
grouped = grouped.astype({
    'Age Category': int,
    'Purchase ID': int,
    'SN': int,
    'Purchase Count': int,
    'Gender': int,
    'Item ID': int,
    'Item Name': int,
    'Price': int,
    'Total_Purchase_Value': float,
    'Average_Purchase_Price': float
})

# Rename columns to match target schema exactly
grouped = grouped.rename(columns={
    'Total_Purchase_Value': 'Total Purchase Value',
    'Average_Purchase_Price': 'Average Purchase Price'
})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_53/target_multisource_mcts.csv", index=False)