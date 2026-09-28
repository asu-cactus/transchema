import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv", index_col=0)

# Convert 'Gender' to string (already string)
df0['Gender'] = df0['Gender'].astype(str)

# Group by 'Gender' and count the number of 'Purchase ID' per Gender
result = df0.groupby('Gender', as_index=False).agg({'Purchase ID': 'count'})

# Rename the aggregated column to match target schema columns for all numeric columns
# The target schema has all columns except Gender as integers with the same value per row.
# So fill all other columns with the count value.

result['SN'] = result['Purchase ID']
result['Age'] = result['Purchase ID']
result['Item ID'] = result['Purchase ID']
result['Item Name'] = result['Purchase ID']
result['Price'] = result['Purchase ID']

# Reorder columns to match target schema
result = result[['Gender', 'Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']]

# Ensure integer types for all numeric columns
for col in ['Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']:
    result[col] = result[col].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)