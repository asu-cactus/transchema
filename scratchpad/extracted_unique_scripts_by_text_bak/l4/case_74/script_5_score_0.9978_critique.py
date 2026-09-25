import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv", index_col=0)

df0['Gender'] = df0['Gender'].astype(str)

# Count number of rows per Gender
count_df = df0.groupby('Gender', as_index=False).size().rename(columns={'size': 'count'})

# Assign count to all numeric columns in target schema
result = count_df.copy()
result['Purchase ID'] = result['count']
result['SN'] = result['count']
result['Age'] = result['count']
result['Item ID'] = result['count']
result['Item Name'] = result['count']
result['Price'] = result['count']

# Drop the temporary 'count' column
result = result.drop(columns=['count'])

# Reorder columns as per target schema
result = result[['Gender', 'Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']]

# Ensure integer type for numeric columns
for col in ['Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']:
    result[col] = result[col].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)