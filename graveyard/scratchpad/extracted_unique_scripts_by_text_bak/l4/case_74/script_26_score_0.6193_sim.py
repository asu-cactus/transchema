import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv", index_col=0)

df0['Purchase ID'] = df0['Purchase ID'].astype(int)
df0['SN'] = pd.to_numeric(df0['SN'], errors='coerce').fillna(0).astype(int)
df0['Age'] = df0['Age'].astype(int)
df0['Item ID'] = df0['Item ID'].astype(int)
df0['Item Name'] = pd.to_numeric(df0['Item Name'], errors='coerce').fillna(0).astype(int)
df0['Price'] = df0['Price'].astype(int)
df0['Gender'] = df0['Gender'].astype(str)

df0 = df0[['Gender', 'Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']]

df0.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)