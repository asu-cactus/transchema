import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_53/training_0.csv", index_col=0)

def age_category(age):
    return int(age)

df0['Age Category'] = df0['Age'].apply(age_category)

agg = df0.groupby('Age Category').agg(
    Purchase_Count=('Purchase ID', 'count'),
    Purchase_ID=('Purchase ID', 'first'),
    SN=('SN', 'first'),
    Gender=('Gender', 'first'),
    Item_ID=('Item ID', 'first'),
    Item_Name=('Item Name', 'first'),
    Price=('Price', 'first'),
    Total_Purchase_Value=('Price', 'sum'),
    Average_Purchase_Price=('Price', 'mean')
).reset_index()

agg = agg.rename(columns={
    'Age Category': 'Age Category',
    'Purchase_ID': 'Purchase ID',
    'Purchase_Count': 'Purchase Count',
    'Item_ID': 'Item ID',
    'Item_Name': 'Item Name',
    'Total_Purchase_Value': 'Total Purchase Value',
    'Average_Purchase_Price': 'Average Purchase Price'
})

agg['Age Category'] = agg['Age Category'].astype(int)
agg['Purchase ID'] = agg['Purchase ID'].astype(int)
agg['SN'] = agg['SN'].astype(str)
agg['Purchase Count'] = agg['Purchase Count'].astype(int)
agg['Gender'] = agg['Gender'].astype(str)
agg['Item ID'] = agg['Item ID'].astype(int)
agg['Item Name'] = agg['Item Name'].astype(str)
agg['Price'] = agg['Price'].astype(float)
agg['Total Purchase Value'] = agg['Total Purchase Value'].astype(float)
agg['Average Purchase Price'] = agg['Average Purchase Price'].astype(float)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_53/target_multisource_mcts.csv", index=False)