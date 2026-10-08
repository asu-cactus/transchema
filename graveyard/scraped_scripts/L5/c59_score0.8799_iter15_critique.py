import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_59/training_0.csv", index_col=0)

# Create Purchase Count as purchase number per customer (SN)
df0['Purchase Count'] = df0.groupby('SN').cumcount() + 1

# Rename Price to Item Price for clarity
df0.rename(columns={'Price': 'Item Price'}, inplace=True)

# Group by Purchase Count and Item Price
# Aggregate Total Purchase Value as sum of Price * count of purchases
# Since each row is one purchase, count of purchases = number of rows per group
grouped = df0.groupby(['Purchase Count', 'Item Price'], as_index=False).agg(
    Total_Purchase_Value=('Item Price', 'size')  # count of purchases per group
)

# Total Purchase Value = Item Price * count of purchases
grouped['Total Purchase Value'] = grouped['Item Price'] * grouped['Total_Purchase_Value']

# Drop the intermediate count column
grouped.drop(columns=['Total_Purchase_Value'], inplace=True)

# Cast columns to correct types
grouped['Purchase Count'] = grouped['Purchase Count'].astype(int)
grouped['Item Price'] = grouped['Item Price'].astype(int)
grouped['Total Purchase Value'] = grouped['Total Purchase Value'].astype(float)

# Reorder columns to match target schema
result = grouped[['Purchase Count', 'Item Price', 'Total Purchase Value']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_59/target_multisource_mcts.csv", index=False)