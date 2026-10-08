import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_82/training_0.csv", index_col=0)

df0['Gender'] = df0['Gender'].map({'Male': 1, 'Female': 4}).astype('Int64')

df0['SN'] = df0['SN'].str.extract('(\d+)').astype('Int64')

df0.rename(columns={'Price': 'Item Price'}, inplace=True)

df0['Purchase ID_x'] = df0['Purchase ID']
df0['Age_x'] = df0['Age']
df0['Purchase Count'] = 1
df0['Purchase ID_y'] = df0['Purchase ID'].astype(float)
df0['Age_y'] = df0['Age'].astype(float)
df0['Purchase ID'] = df0['Purchase ID']
df0['Age'] = df0['Age']

df0['Total Purchase Value'] = df0['Purchase Count'] * df0['Item Price']

group_cols = ['Item ID', 'Item Name', 'Purchase ID_x', 'SN', 'Age_x', 'Gender']

agg_dict = {
    'Purchase Count': 'sum',
    'Purchase ID_y': 'first',
    'Age_y': 'first',
    'Item Price': 'mean',
    'Purchase ID': 'first',
    'Age': 'first',
    'Total Purchase Value': 'sum'
}

df_grouped = df0.groupby(group_cols, as_index=False).agg(agg_dict)

target_cols = ['Item ID', 'Item Name', 'Purchase ID_x', 'SN', 'Age_x', 'Gender', 'Purchase Count',
               'Purchase ID_y', 'Age_y', 'Item Price', 'Purchase ID', 'Age', 'Total Purchase Value']

df_target = df_grouped[target_cols]

df_target.to_csv("autopipeline-benchmarks/github-pipelines/length5_82/target_multisource_mcts.csv", index=False)