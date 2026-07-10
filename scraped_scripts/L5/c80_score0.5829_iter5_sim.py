import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_80/training_0.csv", index_col=0)

df_unpivot = df0.melt(id_vars=['Purchase ID', 'Item ID'], value_vars=['Price'], var_name='Item Name', value_name='Price_x')

df_unpivot['Purchase ID_x'] = df_unpivot['Purchase ID']
df_unpivot['Age_x'] = df0.set_index(['Purchase ID', 'Item ID']).loc[df_unpivot.set_index(['Purchase ID', 'Item ID']).index, 'Age'].values
df_unpivot['Item ID_x'] = df_unpivot['Item ID']

df_unpivot['Price_y'] = df_unpivot['Price_x'].astype(float)
df_unpivot['Item ID_y'] = df_unpivot['Item ID_x']
df_unpivot['Purchase ID_y'] = df_unpivot['Purchase ID_x']
df_unpivot['Age_y'] = df_unpivot['Age_x']

df_unpivot['Item Name'] = df0['Item Name']
df_unpivot['SN'] = df0['SN']
df_unpivot['Age'] = df0['Age']
df_unpivot['Gender'] = df0['Gender']
df_unpivot['Item ID'] = df0['Item ID']
df_unpivot['Purchase ID'] = df0['Purchase ID']
df_unpivot['Price_x'] = df0['Price'].astype(int)

df_unpivot = df_unpivot[['Item Name', 'Purchase ID', 'SN', 'Age', 'Gender', 'Item ID', 'Price_x', 'Purchase ID_x', 'Age_x', 'Item ID_x', 'Price_y', 'Item ID_y', 'Purchase ID_y', 'Age_y']]

df_unpivot.to_csv("autopipeline-benchmarks/github-pipelines/length5_80/target_multisource_mcts.csv", index=False)