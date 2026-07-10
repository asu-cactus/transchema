import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_45/training_0.csv", index_col=0)

agg = df0.groupby(['Gender', 'SN']).agg(
    Purchase_Count=('Purchase ID', 'count'),
    Price_min=('Price', 'min'),
    Price_max=('Price', 'max')
).reset_index()

agg.rename(columns={
    'Purchase_Count': 'Purchase Count',
    'Price_min': 'Age_x',
    'Price_max': 'Item ID_x'
}, inplace=True)

agg['Item Name'] = agg['Price'] = agg['Purchase ID_x'] = agg['Age_y'] = agg['Item ID_y'] = agg['Average Purchase Price'] = agg['Purchase ID_y'] = agg['Age'] = agg['Item ID'] = agg['Total Purchase Value'] = pd.NA

agg = agg[['Gender', 'Purchase Count', 'SN', 'Age_x', 'Item ID_x', 'Item Name', 'Price', 'Purchase ID_x', 'Age_y', 'Item ID_y', 'Average Purchase Price', 'Purchase ID_y', 'Age', 'Item ID', 'Total Purchase Value']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_45/target_multisource_mcts.csv", index=False)