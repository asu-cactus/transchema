import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv", index_col=0)

# Group by 'Gender' and count 'Purchase ID'
agg_df = df0.groupby('Gender', as_index=False).agg({'Purchase ID': 'count'})

# Rename the count column to 'Purchase ID'
agg_df.rename(columns={'Purchase ID': 'count'}, inplace=True)

# Assign the count value to all required columns as integers
agg_df['Purchase ID'] = agg_df['count']
agg_df['SN'] = agg_df['count']
agg_df['Age'] = agg_df['count']
agg_df['Item ID'] = agg_df['count']
agg_df['Item Name'] = agg_df['count']
agg_df['Price'] = agg_df['count']

# Keep only the target columns in order
result_df = agg_df[['Gender', 'Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']]

# Ensure correct dtypes
result_df['Purchase ID'] = result_df['Purchase ID'].astype(int)
result_df['SN'] = result_df['SN'].astype(int)
result_df['Age'] = result_df['Age'].astype(int)
result_df['Item ID'] = result_df['Item ID'].astype(int)
result_df['Item Name'] = result_df['Item Name'].astype(int)
result_df['Price'] = result_df['Price'].astype(int)

result_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)