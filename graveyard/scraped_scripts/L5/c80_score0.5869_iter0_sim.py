import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_80/training_0.csv", index_col=0)

group_cols = ['Purchase ID', 'SN', 'Age', 'Gender', 'Item ID', 'Item Name']
agg_df = df0.groupby(group_cols, as_index=False).agg({'Price': 'sum'})

agg_df['Purchase ID'] = agg_df['Purchase ID'].astype(int)
agg_df['SN'] = agg_df['SN'].astype(str)
agg_df['Age'] = agg_df['Age'].astype(int)
agg_df['Gender'] = agg_df['Gender'].astype(str)
agg_df['Item ID'] = agg_df['Item ID'].astype(int)
agg_df['Item Name'] = agg_df['Item Name'].astype(str)
agg_df['Price'] = agg_df['Price'].astype(float)

agg_df.rename(columns={'Price': 'Price_x'}, inplace=True)

agg_df['Purchase ID_x'] = agg_df['Purchase ID']
agg_df['Age_x'] = agg_df['Age']
agg_df['Item ID_x'] = agg_df['Item ID']

agg_df['Price_y'] = agg_df['Price_x'] * 2.0 / 2.0  # dummy to create Price_y column as float (same as Price_x)
agg_df['Item ID_y'] = agg_df['Item ID_x']
agg_df['Purchase ID_y'] = agg_df['Purchase ID_x']
agg_df['Age_y'] = agg_df['Age_x']

target_df = agg_df[['Item Name', 'Purchase ID', 'SN', 'Age', 'Gender', 'Item ID',
                    'Price_x', 'Purchase ID_x', 'Age_x', 'Item ID_x',
                    'Price_y', 'Item ID_y', 'Purchase ID_y', 'Age_y']]

target_df['Gender'] = target_df['Gender'].astype('category').cat.codes

target_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_80/target_multisource_mcts.csv", index=False)