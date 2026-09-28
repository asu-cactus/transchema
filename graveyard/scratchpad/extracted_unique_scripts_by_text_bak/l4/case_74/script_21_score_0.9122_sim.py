import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv", index_col=0)

df0['Purchase ID'] = pd.to_numeric(df0['Purchase ID'], errors='coerce').fillna(0).astype(int)
df0['SN'] = pd.to_numeric(df0['SN'], errors='coerce').fillna(0).astype(int)
df0['Age'] = pd.to_numeric(df0['Age'], errors='coerce').fillna(0).astype(int)
df0['Item ID'] = pd.to_numeric(df0['Item ID'], errors='coerce').fillna(0).astype(int)
df0['Item Name'] = pd.to_numeric(df0['Item Name'], errors='coerce').fillna(0).astype(int)
df0['Price'] = pd.to_numeric(df0['Price'], errors='coerce').fillna(0).astype(int)
df0['Gender'] = df0['Gender'].astype(str)

result = df0.groupby('Gender', as_index=False).agg({
    'Purchase ID': 'sum',
    'SN': 'sum',
    'Age': 'sum',
    'Item ID': 'sum',
    'Item Name': 'sum',
    'Price': 'sum'
})

result = result[['Gender', 'Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)