import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_80/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_80/training_0.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True)

df['Purchase ID'] = pd.to_numeric(df['Purchase ID'], errors='coerce').astype('Int64')
df['SN'] = pd.to_numeric(df['SN'], errors='coerce', downcast='integer')
df['Age'] = pd.to_numeric(df['Age'], errors='coerce').astype('Int64')
df['Gender'] = df['Gender'].map({'Male':1, 'Female':2}).astype('Int64')
df['Item ID'] = pd.to_numeric(df['Item ID'], errors='coerce').astype('Int64')
df['Price'] = pd.to_numeric(df['Price'], errors='coerce')

df = df.rename(columns={
    'Price': 'Price_x',
    'Purchase ID': 'Purchase ID_x',
    'Age': 'Age_x',
    'Item ID': 'Item ID_x',
    'Item Name': 'Item Name',
    'SN': 'SN',
    'Gender': 'Gender'
})

df['Purchase ID_y'] = df['Purchase ID_x']
df['Age_y'] = df['Age_x']
df['Item ID_y'] = df['Item ID_x']
df['Price_y'] = df['Price_x']

df['Purchase ID'] = df['Purchase ID_x']
df['Age'] = df['Age_x']
df['Item ID'] = df['Item ID_x']
df['Price_x'] = df['Price_x']

target_cols = ['Item Name', 'Purchase ID', 'SN', 'Age', 'Gender', 'Item ID',
               'Price_x', 'Purchase ID_x', 'Age_x', 'Item ID_x',
               'Price_y', 'Item ID_y', 'Purchase ID_y', 'Age_y']

df_target = df[target_cols]

df_target.to_csv("autopipeline-benchmarks/github-pipelines/length5_80/target_multisource_mcts.csv", index=False)