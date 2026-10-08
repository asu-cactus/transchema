import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv", index_col=0)

df = df0.copy()
df['Purchase ID'] = pd.to_numeric(df['Purchase ID'], errors='coerce').fillna(0).astype(int)
df['SN'] = pd.to_numeric(df['SN'], errors='coerce').fillna(0).astype(int)
df['Age'] = pd.to_numeric(df['Age'], errors='coerce').fillna(0).astype(int)
df['Item ID'] = pd.to_numeric(df['Item ID'], errors='coerce').fillna(0).astype(int)
df['Item Name'] = pd.to_numeric(df['Item Name'], errors='coerce').fillna(0).astype(int)
df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0).astype(int)
df['Gender'] = df['Gender'].astype(str)

grouped = df.groupby('Gender').agg({
    'Purchase ID': 'sum',
    'SN': 'sum',
    'Age': 'sum',
    'Item ID': 'sum',
    'Item Name': 'sum',
    'Price': 'sum'
}).reset_index()

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)