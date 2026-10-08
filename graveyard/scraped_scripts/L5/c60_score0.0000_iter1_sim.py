import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_60/training_0.csv", index_col=0)

df_joined = df0.merge(df0, on="Purchase ID", suffixes=('_x', '_y'))

df_joined['Purchase Count'] = df_joined.groupby('Purchase ID')['Purchase ID'].transform('count')

df_joined['Purchase ID_x'] = df_joined['Purchase ID_x'].astype(float)
df_joined['Purchase ID_y'] = df_joined['Purchase ID_y'].astype(int)

df_joined['Item ID_x'] = df_joined['Item ID_x'].astype(int)
df_joined['Item ID_y'] = df_joined['Item ID_y'].astype(float)

df_joined['Age_x'] = df_joined['Age_x'].astype(int)
df_joined['Age_y'] = df_joined['Age_y'].astype(int)
df_joined['Age'] = df_joined['Age'].astype(int)

df_joined['Gender'] = df_joined['Gender_x'].map({'Male':1, 'Female':0}).astype(int)

df_joined['SN'] = df_joined['SN_x'].str.extract('(\d+)').astype(int)

df_joined['Item Name'] = df_joined['Item Name_x'].astype('category').cat.codes

df_joined['Price'] = df_joined['Price_x'].astype(int)

df_joined['Average Purchase Price'] = df_joined.groupby('Purchase ID')['Price_x'].transform('mean')

df_joined['Total Purchase Value'] = df_joined['Purchase Count'] * df_joined['Average Purchase Price']

target_cols = ['Purchase Count', 'SN', 'Age_x', 'Gender', 'Item ID_x', 'Item Name', 'Price',
               'Purchase ID_x', 'Age_y', 'Item ID_y', 'Average Purchase Price', 'Purchase ID_y',
               'Age', 'Item ID', 'Total Purchase Value']

df_joined['Item ID'] = df_joined['Item ID_x']

result = df_joined[target_cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_60/target_multisource_mcts.csv", index=False)