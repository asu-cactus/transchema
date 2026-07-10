import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_60/training_0.csv", index_col=0)

group_cols = ['SN', 'Age', 'Gender', 'Item ID', 'Item Name', 'Price']

agg_df = df0.groupby(group_cols).agg(
    Purchase_Count=('Purchase ID', 'count'),
    Purchase_ID_x=('Purchase ID', 'mean'),
    Age_y=('Age', 'mean'),
    Item_ID_y=('Item ID', 'mean'),
    Average_Purchase_Price=('Price', 'mean'),
    Purchase_ID_y=('Purchase ID', 'max'),
    Total_Purchase_Value=('Price', 'sum')
).reset_index()

agg_df.rename(columns={
    'Age': 'Age_x',
    'Item ID': 'Item ID_x',
    'Purchase_Count': 'Purchase Count',
    'Purchase_ID_x': 'Purchase ID_x',
    'Age_y': 'Age_y',
    'Item_ID_y': 'Item ID_y',
    'Average_Purchase_Price': 'Average Purchase Price',
    'Purchase_ID_y': 'Purchase ID_y',
    'Total_Purchase_Value': 'Total Purchase Value'
}, inplace=True)

agg_df['Age_x'] = agg_df['Age_x'].astype(int)
agg_df['Gender'] = agg_df['Gender'].astype('category').cat.codes
agg_df['Item ID_x'] = agg_df['Item ID_x'].astype(int)
agg_df['Purchase Count'] = agg_df['Purchase Count'].astype(int)
agg_df['Age_y'] = agg_df['Age_y'].astype(int)
agg_df['Item ID_y'] = agg_df['Item ID_y'].astype(int)
agg_df['Purchase ID_y'] = agg_df['Purchase ID_y'].astype(int)
agg_df['SN'] = agg_df['SN'].astype('category').cat.codes
agg_df['Item Name'] = agg_df['Item Name'].astype(str)
agg_df['Price'] = agg_df['Price'].astype(int)

agg_df['Age'] = agg_df['Age_x']
agg_df['Item ID'] = agg_df['Item ID_x']

cols_order = ['Purchase Count', 'SN', 'Age_x', 'Gender', 'Item ID_x', 'Item Name', 'Price',
              'Purchase ID_x', 'Age_y', 'Item ID_y', 'Average Purchase Price', 'Purchase ID_y',
              'Age', 'Item ID', 'Total Purchase Value']

agg_df = agg_df[cols_order]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_60/target_multisource_mcts.csv", index=False)