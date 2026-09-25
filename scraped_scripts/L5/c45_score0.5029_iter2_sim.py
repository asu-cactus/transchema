import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_45/training_0.csv", index_col=0)

df = df0.copy()

df.rename(columns={
    'Purchase ID': 'Purchase ID_x',
    'Item ID': 'Item ID_x',
    'Item Name': 'Item Name',
    'Price': 'Price',
    'SN': 'SN',
    'Age': 'Age_x',
    'Gender': 'Gender'
}, inplace=True)

df['Purchase Count'] = 1
df['Age_y'] = df['Age_x'].astype(float)
df['Item ID_y'] = df['Item ID_x'].astype(float)
df['Average Purchase Price'] = df['Price'].astype(float)
df['Purchase ID_y'] = df['Purchase ID_x'].astype(int)
df['Age'] = df['Age_x'].astype(int)
df['Item ID'] = df['Item ID_x'].astype(int)
df['Total Purchase Value'] = df['Price'].astype(float)

df = df[['Gender', 'Purchase Count', 'SN', 'Age_x', 'Item ID_x', 'Item Name', 'Price', 'Purchase ID_x',
         'Age_y', 'Item ID_y', 'Average Purchase Price', 'Purchase ID_y', 'Age', 'Item ID', 'Total Purchase Value']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_45/target_multisource_mcts.csv", index=False)