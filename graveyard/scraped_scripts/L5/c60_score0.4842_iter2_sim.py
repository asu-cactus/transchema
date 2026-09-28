import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_60/training_0.csv", index_col=0)

pivot_df = df0.pivot_table(index='Purchase ID', aggfunc='first').reset_index()

joined_df = pd.merge(df0, df0, on='Purchase ID', suffixes=('_x', '_y'))

joined_df['Purchase ID_x'] = joined_df['Purchase ID'].astype(float)
joined_df['Purchase ID_y'] = joined_df['Purchase ID'].astype(int)

joined_df['Item ID_y'] = joined_df['Item ID_y'].astype(float)
joined_df['Average Purchase Price'] = joined_df['Price_y'] / joined_df['Purchase Count'] if 'Purchase Count' in joined_df else joined_df['Price_y']

joined_df['Purchase Count'] = joined_df.groupby('Purchase ID_x')['Purchase ID_x'].transform('count')
joined_df['Total Purchase Value'] = joined_df['Price_x'] * joined_df['Purchase Count']

joined_df['SN'] = pd.factorize(joined_df['SN_x'])[0] + 1
joined_df['Age_x'] = joined_df['Age_x'].astype(int)
joined_df['Gender'] = pd.factorize(joined_df['Gender_x'])[0] + 1
joined_df['Item ID_x'] = joined_df['Item ID_x'].astype(int)
joined_df['Item Name'] = pd.factorize(joined_df['Item Name_x'])[0] + 1
joined_df['Price'] = joined_df['Price_x'].astype(int)
joined_df['Age_y'] = joined_df['Age_y'].astype(int)
joined_df['Age'] = joined_df['Age_x'].astype(int)
joined_df['Item ID'] = joined_df['Item ID_x'].astype(int)

result = joined_df[['Purchase Count', 'SN', 'Age_x', 'Gender', 'Item ID_x', 'Item Name', 'Price', 'Purchase ID_x',
                    'Age_y', 'Item ID_y', 'Average Purchase Price', 'Purchase ID_y', 'Age', 'Item ID', 'Total Purchase Value']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_60/target_multisource_mcts.csv", index=False)