import pandas as pd

# Read source table
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_53/training_0.csv", index_col=0)

# Create Age Category as integer from Age
df0['Age Category'] = df0['Age'].astype(int)

# Encode SN as integer (factorize)
df0['SN'], _ = pd.factorize(df0['SN'])

# Encode Gender as integer (factorize)
df0['Gender'], _ = pd.factorize(df0['Gender'])

# Encode Item Name as integer (factorize)
df0['Item Name'], _ = pd.factorize(df0['Item Name'])

# Group by the leftmost columns of target schema that are non-float and unique
group_cols = ['Age Category', 'Purchase ID', 'SN', 'Gender', 'Item ID', 'Item Name', 'Price']

agg = df0.groupby(group_cols).agg(
    Purchase_Count=('Purchase ID', 'count'),
    Total_Purchase_Value=('Price', 'sum'),
    Average_Purchase_Price=('Price', 'mean')
).reset_index()

# Rename columns to match target schema exactly
agg = agg.rename(columns={
    'Purchase_Count': 'Purchase Count',
    'Total_Purchase_Value': 'Total Purchase Value',
    'Average_Purchase_Price': 'Average Purchase Price'
})

# Cast columns to correct types
agg['Age Category'] = agg['Age Category'].astype(int)
agg['Purchase ID'] = agg['Purchase ID'].astype(int)
agg['SN'] = agg['SN'].astype(int)
agg['Purchase Count'] = agg['Purchase Count'].astype(int)
agg['Gender'] = agg['Gender'].astype(int)
agg['Item ID'] = agg['Item ID'].astype(int)
agg['Item Name'] = agg['Item Name'].astype(int)
agg['Price'] = agg['Price'].astype(float)
agg['Total Purchase Value'] = agg['Total Purchase Value'].astype(float)
agg['Average Purchase Price'] = agg['Average Purchase Price'].astype(float)

# Write output
agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_53/target_multisource_mcts.csv", index=False)