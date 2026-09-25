import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_82/training_0.csv", index_col=0)

# Map Gender to int
df0['Gender'] = df0['Gender'].map({'Male': 1, 'Female': 2}).fillna(0).astype(int)

# Encode SN to integer codes
df0['SN'] = pd.factorize(df0['SN'])[0] + 1  # start from 1 to match target style

agg_df = df0.groupby(['Item ID', 'Item Name']).agg(
    Purchase_ID_x=('Purchase ID', 'count'),
    SN=('SN', 'first'),
    Age_x=('Age', 'max'),
    Gender=('Gender', 'max'),
    Purchase_Count=('Purchase ID', 'count'),
    Purchase_ID_y=('Purchase ID', 'mean'),
    Age_y=('Age', 'mean'),
    Item_Price=('Price', 'mean'),
    Purchase_ID=('Purchase ID', 'max'),
    Age=('Age', 'max'),
    Total_Purchase_Value=('Price', 'sum')
).reset_index()

# Rename columns to match target schema exactly
agg_df = agg_df.rename(columns={
    'Item ID': 'Item ID',
    'Item Name': 'Item Name',
    'Purchase_ID_x': 'Purchase ID_x',
    'SN': 'SN',
    'Age_x': 'Age_x',
    'Gender': 'Gender',
    'Purchase_Count': 'Purchase Count',
    'Purchase_ID_y': 'Purchase ID_y',
    'Age_y': 'Age_y',
    'Item_Price': 'Item Price',
    'Purchase_ID': 'Purchase ID',
    'Age': 'Age',
    'Total_Purchase_Value': 'Total Purchase Value'
})

# Cast columns to correct types
agg_df = agg_df.astype({
    'Item ID': 'int64',
    'Item Name': 'object',
    'Purchase ID_x': 'int64',
    'SN': 'int64',
    'Age_x': 'int64',
    'Gender': 'int64',
    'Purchase Count': 'int64',
    'Purchase ID_y': 'float64',
    'Age_y': 'float64',
    'Item Price': 'float64',
    'Purchase ID': 'int64',
    'Age': 'int64',
    'Total Purchase Value': 'float64'
})

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_82/target_multisource_mcts.csv", index=False)