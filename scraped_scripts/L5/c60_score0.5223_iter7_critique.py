import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_60/training_0.csv", index_col=0)

# Map SN and Gender to integer codes to match target schema
df0['SN_int'] = pd.factorize(df0['SN'])[0] + 1
df0['Gender_int'] = pd.factorize(df0['Gender'])[0] + 1

# Self join on SN to produce _x and _y columns
df_join = df0.merge(df0, on='SN', suffixes=('_x', '_y'))

# Use integer codes for grouping
df_join['SN'] = df_join['SN_int_x']
df_join['Gender'] = df_join['Gender_int_x']

agg = df_join.groupby(['SN', 'Gender']).agg(
    Purchase_Count=('Purchase ID_x', 'count'),
    Age_x=('Age_x', 'first'),
    Item_ID_x=('Item ID_x', 'first'),
    Item_Name=('Item Name_x', 'first'),
    Price=('Price_x', 'first'),
    Purchase_ID_x=('Purchase ID_x', 'first'),
    Age_y=('Age_y', 'first'),
    Item_ID_y=('Item ID_y', 'mean'),
    Average_Purchase_Price=('Price_y', 'mean'),
    Purchase_ID_y=('Purchase ID_y', 'count'),
    Age=('Age_x', 'sum'),
    Item_ID=('Item ID_x', 'sum'),
    Total_Purchase_Value=('Price_x', 'sum')
).reset_index()

agg = agg.rename(columns={
    'Purchase_Count': 'Purchase Count',
    'SN': 'SN',
    'Age_x': 'Age_x',
    'Gender': 'Gender',
    'Item_ID_x': 'Item ID_x',
    'Item_Name': 'Item Name',
    'Price': 'Price',
    'Purchase_ID_x': 'Purchase ID_x',
    'Age_y': 'Age_y',
    'Item_ID_y': 'Item ID_y',
    'Average_Purchase_Price': 'Average Purchase Price',
    'Purchase_ID_y': 'Purchase ID_y',
    'Age': 'Age',
    'Item_ID': 'Item ID',
    'Total_Purchase_Value': 'Total Purchase Value'
})

agg['Purchase Count'] = agg['Purchase Count'].astype(int)
agg['SN'] = agg['SN'].astype(int)
agg['Age_x'] = agg['Age_x'].astype(int)
agg['Gender'] = agg['Gender'].astype(int)
agg['Item ID_x'] = agg['Item ID_x'].astype(int)
agg['Item Name'] = agg['Item Name'].astype(str)
agg['Price'] = agg['Price'].astype(float)
agg['Purchase ID_x'] = agg['Purchase ID_x'].astype(float)
agg['Age_y'] = agg['Age_y'].astype(int)
agg['Item ID_y'] = agg['Item ID_y'].astype(float)
agg['Average Purchase Price'] = agg['Average Purchase Price'].astype(float)
agg['Purchase ID_y'] = agg['Purchase ID_y'].astype(int)
agg['Age'] = agg['Age'].astype(int)
agg['Item ID'] = agg['Item ID'].astype(int)
agg['Total Purchase Value'] = agg['Total Purchase Value'].astype(float)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_60/target_multisource_mcts.csv", index=False)