import pandas as pd

# Read source table
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_53/training_0.csv", index_col=0)

# Create Age Category as integer from Age
df0['Age Category'] = df0['Age'].astype(int)

# Encode categorical columns to integers
# For SN
df0['SN'] = pd.factorize(df0['SN'])[0] + 1  # +1 to avoid zero if needed

# For Gender
df0['Gender'] = pd.factorize(df0['Gender'])[0] + 1

# For Item Name
df0['Item Name'] = pd.factorize(df0['Item Name'])[0] + 1

# Convert Price to integer for grouping (target schema has Price as int)
df0['Price'] = df0['Price'].astype(int)

# Group by the leftmost columns (excluding Purchase Count which is aggregation)
group_cols = ['Age Category', 'Purchase ID', 'SN', 'Gender', 'Item ID', 'Item Name', 'Price']

agg_df = df0.groupby(group_cols).agg(
    Purchase_Count=('Purchase ID', 'count'),
    Total_Purchase_Value=('Price', 'sum'),
    Average_Purchase_Price=('Price', 'mean')
).reset_index()

# Rename columns to match target schema exactly
agg_df = agg_df.rename(columns={
    'Purchase_Count': 'Purchase Count',
    'Total_Purchase_Value': 'Total Purchase Value',
    'Average_Purchase_Price': 'Average Purchase Price'
})

# Ensure correct column order as target schema
agg_df = agg_df[['Age Category', 'Purchase ID', 'SN', 'Purchase Count', 'Gender', 'Item ID', 'Item Name', 'Price', 'Total Purchase Value', 'Average Purchase Price']]

# Write to output CSV
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_53/target_multisource_mcts.csv", index=False)