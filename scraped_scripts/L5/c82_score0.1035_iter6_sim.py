import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_82/training_0.csv", index_col=0)

df0['Gender'] = df0['Gender'].astype(str).str.strip()
gender_map = {g: i for i, g in enumerate(sorted(df0['Gender'].unique()), 1)}
df0['Gender'] = df0['Gender'].map(gender_map)

agg = df0.groupby('Gender').agg(
    Purchase_Count=('Purchase ID', 'count'),
    Total_Purchase_Value=('Price', 'sum')
).reset_index()

agg['Purchase Count'] = agg['Purchase_Count']
agg['Total Purchase Value'] = agg['Total_Purchase_Value']

agg = agg.drop(columns=['Purchase_Count', 'Total_Purchase_Value'])

agg['Item ID'] = 0
agg['Item Name'] = ''
agg['Purchase ID_x'] = 0
agg['SN'] = 0
agg['Age_x'] = 0
agg['Purchase ID_y'] = 0.0
agg['Age_y'] = 0.0
agg['Item Price'] = 0.0
agg['Purchase ID'] = 0
agg['Age'] = 0.0

agg = agg[['Item ID', 'Item Name', 'Purchase ID_x', 'SN', 'Age_x', 'Gender', 'Purchase Count',
           'Purchase ID_y', 'Age_y', 'Item Price', 'Purchase ID', 'Age', 'Total Purchase Value']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_82/target_multisource_mcts.csv", index=False)