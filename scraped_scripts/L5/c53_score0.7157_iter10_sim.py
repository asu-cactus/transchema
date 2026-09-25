import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_53/training_0.csv", index_col=0)

grouped = df0.groupby(['Age', 'Gender']).agg(
    Purchase_Count=('Purchase ID', 'count'),
    Total_Purchase_Value=('Price', 'sum'),
    Sum_Price_2=('Price', 'sum')
).reset_index()

grouped['Average_Purchase_Price'] = grouped['Total_Purchase_Value'] / grouped['Purchase_Count']

grouped['Age Category'] = grouped['Age'].astype(int)
grouped['Purchase ID'] = grouped['Purchase_Count'].astype(int)
grouped['SN'] = grouped['Purchase_Count'].astype(int)
grouped['Purchase Count'] = grouped['Purchase_Count'].astype(int)
grouped['Gender'] = grouped['Gender'].astype('category').cat.codes.astype(int)

grouped['Item ID'] = grouped['Purchase_Count'].astype(int)
grouped['Item Name'] = grouped['Purchase_Count'].astype(int)
grouped['Price'] = grouped['Purchase_Count'].astype(int)

result = grouped.rename(columns={
    'Total_Purchase_Value': 'Total Purchase Value',
    'Average_Purchase_Price': 'Average Purchase Price'
})[
    ['Age Category', 'Purchase ID', 'SN', 'Purchase Count', 'Gender', 'Item ID', 'Item Name', 'Price', 'Total Purchase Value', 'Average Purchase Price']
]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_53/target_multisource_mcts.csv", index=False)