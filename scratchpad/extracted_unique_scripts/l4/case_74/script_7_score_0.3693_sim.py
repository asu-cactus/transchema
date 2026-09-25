import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv", index_col=0)

df0['SN'] = pd.to_numeric(df0['SN'], errors='coerce')
df0['Purchase ID'] = pd.to_numeric(df0['Purchase ID'], errors='coerce')
df0['Age'] = pd.to_numeric(df0['Age'], errors='coerce')
df0['Item ID'] = pd.to_numeric(df0['Item ID'], errors='coerce')
df0['Item Name'] = pd.to_numeric(df0['Item Name'], errors='coerce')
df0['Price'] = pd.to_numeric(df0['Price'], errors='coerce')

df = df0[['Gender', 'Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)