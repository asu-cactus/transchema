import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_45/training_0.csv", index_col=0)

df_unpivot = df0.melt(id_vars=['Gender'], value_vars=['Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price'], var_name='variable', value_name='value')

agg_funcs = {
    'Purchase ID': ['count', 'mean', 'sum'],
    'SN': 'count',
    'Age': ['mean', 'min', 'max'],
    'Item ID': ['mean', 'min', 'max'],
    'Item Name': 'count',
    'Price': ['mean', 'sum']
}

agg_df = df0.groupby('Gender').agg({
    'Purchase ID': ['count', 'mean', 'sum'],
    'SN': 'count',
    'Age': ['mean', 'min', 'max'],
    'Item ID': ['mean', 'min', 'max'],
    'Item Name': 'count',
    'Price': ['mean', 'sum']
})

agg_df.columns = ['Purchase Count', 'Purchase ID_y', 'Total Purchase Value', 'SN', 'Age_y', 'Age_x', 'Age', 'Item ID_y', 'Item ID_x', 'Item ID', 'Item Name', 'Average Purchase Price', 'Price']

agg_df = agg_df.reset_index()

agg_df['Purchase ID_x'] = agg_df['Purchase ID_y'].astype(float)
agg_df['Purchase ID_y'] = agg_df['Purchase ID_y'].astype(int)
agg_df['Age_x'] = agg_df['Age_x'].astype(int)
agg_df['Age_y'] = agg_df['Age_y'].astype(float)
agg_df['Age'] = agg_df['Age'].astype(int)
agg_df['Item ID_x'] = agg_df['Item ID_x'].astype(int)
agg_df['Item ID_y'] = agg_df['Item ID_y'].astype(float)
agg_df['Item ID'] = agg_df['Item ID'].astype(int)
agg_df['Item Name'] = agg_df['Item Name'].astype(int)
agg_df['Price'] = agg_df['Price'].astype(int)
agg_df['Average Purchase Price'] = agg_df['Average Purchase Price'].astype(float)
agg_df['Total Purchase Value'] = agg_df['Total Purchase Value'].astype(float)
agg_df['Purchase Count'] = agg_df['Purchase Count'].astype(int)
agg_df['SN'] = agg_df['SN'].astype(int)

agg_df = agg_df[['Gender', 'Purchase Count', 'SN', 'Age_x', 'Item ID_x', 'Item Name', 'Price', 'Purchase ID_x', 'Age_y', 'Item ID_y', 'Average Purchase Price', 'Purchase ID_y', 'Age', 'Item ID', 'Total Purchase Value']]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_45/target_multisource_mcts.csv", index=False)