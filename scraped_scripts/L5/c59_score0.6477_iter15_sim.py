import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_59/training_0.csv", index_col=0)

df0['Purchase Count'] = df0.groupby('SN').cumcount() + 1

pivot_df = df0.pivot_table(index='Purchase Count', columns='Price', values='Purchase ID', aggfunc='count', fill_value=0)

unpivot_df = pivot_df.reset_index().melt(id_vars='Purchase Count', var_name='Item Price', value_name='Purchase ID Count')

df0['Total Purchase Value'] = df0['Price'] * df0['Purchase ID'].map(df0.groupby('Purchase ID')['Purchase ID'].count())

grouped = unpivot_df.merge(df0[['Purchase Count', 'Price', 'Purchase ID']], left_on=['Purchase Count', 'Item Price'], right_on=['Purchase Count', 'Price'], how='left')

grouped['Total Purchase Value'] = grouped['Item Price'] * grouped['Purchase ID Count']

result = grouped.groupby(['Purchase Count', 'Item Price'], as_index=False).agg({'Total Purchase Value':'sum'})

result['Purchase Count'] = result['Purchase Count'].astype(int)
result['Item Price'] = result['Item Price'].astype(int)
result['Total Purchase Value'] = result['Total Purchase Value'].astype(float)

result.rename(columns={'Item Price':'Item Price', 'Total Purchase Value':'Total Purchase Value'}, inplace=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_59/target_multisource_mcts.csv", index=False)