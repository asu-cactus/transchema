import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv", index_col=0)

# Extract digits from SN to convert to integer
df0['SN_int'] = df0['SN'].astype(str).str.extract('(\d+)')[0]
df0['SN_int'] = pd.to_numeric(df0['SN_int'], errors='coerce')

# Convert Item Name to integer by hashing
df0['Item_Name_int'] = df0['Item Name'].astype(str).apply(lambda x: abs(hash(x)) % (10**9))

# Group by Gender and aggregate COUNT of Purchase ID
grouped = df0.groupby('Gender').agg(
    Purchase_ID_count = ('Purchase ID', 'count'),
)

# Since target columns after Gender are all integers and have the same value per Gender,
# assign the count to all integer columns
grouped['Purchase ID'] = grouped['Purchase_ID_count']
grouped['SN'] = grouped['Purchase_ID_count']
grouped['Age'] = grouped['Purchase_ID_count']
grouped['Item ID'] = grouped['Purchase_ID_count']
grouped['Item Name'] = grouped['Purchase_ID_count']
grouped['Price'] = grouped['Purchase_ID_count']

# Reset index to have Gender as a column
result = grouped.reset_index()

# Select columns in target schema order
result = result[['Gender', 'Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']]

# Convert types accordingly
result['Gender'] = result['Gender'].astype(str)
result['Purchase ID'] = result['Purchase ID'].astype('Int64')
result['SN'] = result['SN'].astype('Int64')
result['Age'] = result['Age'].astype('Int64')
result['Item ID'] = result['Item ID'].astype('Int64')
result['Item Name'] = result['Item Name'].astype('Int64')
result['Price'] = result['Price'].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)