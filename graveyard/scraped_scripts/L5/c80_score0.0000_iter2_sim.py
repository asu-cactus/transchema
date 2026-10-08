import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_80/training_0.csv", index_col=0)

df_union = df0.copy()

df_join = pd.merge(df_union, df_union, on=["Purchase ID", "Item ID"], suffixes=('_x', '_y'))

df_join['Purchase ID_x'] = df_join['Purchase ID']
df_join['Purchase ID_y'] = df_join['Purchase ID']
df_join['Age_x'] = df_join['Age_x'].astype('Int64')
df_join['Age_y'] = df_join['Age_y'].astype('Int64')
df_join['Purchase ID_x'] = df_join['Purchase ID_x'].astype('Int64')
df_join['Purchase ID_y'] = df_join['Purchase ID_y'].astype('Int64')
df_join['Purchase ID'] = df_join['Purchase ID'].astype('Int64')
df_join['SN'] = pd.to_numeric(df_join['SN'], errors='coerce').astype('Int64')
df_join['Gender'] = pd.to_numeric(df_join['Gender'], errors='coerce').astype('Int64')
df_join['Item ID_x'] = df_join['Item ID_x'].astype('Int64')
df_join['Item ID_y'] = df_join['Item ID_y'].astype('Int64')
df_join['Item ID'] = df_join['Item ID'].astype('Int64')
df_join['Price_x'] = df_join['Price_x'].astype('Int64')
df_join['Price_y'] = df_join['Price_y'].astype(float)

result = pd.DataFrame()
result['Item Name'] = df_join['Item Name']
result['Purchase ID'] = df_join['Purchase ID']
result['SN'] = df_join['SN']
result['Age'] = df_join['Age']
result['Gender'] = df_join['Gender']
result['Item ID'] = df_join['Item ID']
result['Price_x'] = df_join['Price_x']
result['Purchase ID_x'] = df_join['Purchase ID_x']
result['Age_x'] = df_join['Age_x']
result['Item ID_x'] = df_join['Item ID_x']
result['Price_y'] = df_join['Price_y']
result['Item ID_y'] = df_join['Item ID_y']
result['Purchase ID_y'] = df_join['Purchase ID_y']
result['Age_y'] = df_join['Age_y']

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_80/target_multisource_mcts.csv", index=False)