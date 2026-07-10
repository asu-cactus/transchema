import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_82/training_0.csv", index_col=0)

df0['Purchase ID_x'] = df0['Purchase ID'].astype(int)
df0['SN'] = pd.to_numeric(df0['SN'], errors='coerce')
df0['Age_x'] = pd.to_numeric(df0['Age'], errors='coerce')
df0['Gender'] = df0['Gender'].map({'Male':1, 'Female':2}).fillna(0).astype(int)
df0['Purchase Count'] = 1
df0['Purchase ID_y'] = df0['Price'].astype(float) * 100  # temporary placeholder to create column, will fix below
df0['Age_y'] = df0['Age'].astype(float)
df0['Item Price'] = df0['Price'].astype(float)
df0['Purchase ID'] = df0['Purchase ID'].astype(int)
df0['Age'] = df0['Age'].astype(int)
df0['Total Purchase Value'] = df0['Price'].astype(float)

grouped = df0.groupby('Item Name', as_index=False).agg({
    'Item ID': 'first',
    'Purchase ID_x': 'first',
    'SN': 'first',
    'Age_x': 'first',
    'Gender': 'first',
    'Purchase Count': 'sum',
    'Purchase ID_y': 'first',
    'Age_y': 'first',
    'Item Price': 'first',
    'Purchase ID': 'first',
    'Age': 'first',
    'Total Purchase Value': 'sum'
})

grouped = grouped[['Item ID', 'Item Name', 'Purchase ID_x', 'SN', 'Age_x', 'Gender', 'Purchase Count',
                   'Purchase ID_y', 'Age_y', 'Item Price', 'Purchase ID', 'Age', 'Total Purchase Value']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_82/target_multisource_mcts.csv", index=False)