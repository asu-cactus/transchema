import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv", index_col=0)

df = df0.copy()

df['Gender'] = df['Gender'].astype(str)
df['Purchase ID'] = pd.to_numeric(df['Purchase ID'], errors='coerce').astype('Int64')
df['SN'] = pd.to_numeric(df['SN'], errors='coerce').astype('Int64')
df['Age'] = pd.to_numeric(df['Age'], errors='coerce').astype('Int64')
df['Item ID'] = pd.to_numeric(df['Item ID'], errors='coerce').astype('Int64')
df['Item Name'] = pd.to_numeric(df['Item Name'], errors='coerce').astype('Int64')
df['Price'] = pd.to_numeric(df['Price'], errors='coerce').astype('Int64')

df = df[['Gender', 'Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)