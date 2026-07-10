import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv", index_col=0)

grouped = df0.groupby(['Purchase ID', 'SN', 'Age', 'Gender', 'Item ID'], as_index=False).agg(
    Item_Name=('Item Name', 'count'),
    Price_sum=('Price', 'sum'),
    Price_avg=('Price', 'mean')
)

grouped['Item Name'] = grouped['Item_Name'].astype(int)
grouped['Price'] = grouped['Price_sum'].add(grouped['Price_avg']).astype(int)

result = grouped[['Gender', 'Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)