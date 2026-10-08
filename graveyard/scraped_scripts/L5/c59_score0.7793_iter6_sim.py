import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_59/training_0.csv", index_col=0)

df = df0.copy()
df['Purchase Count'] = 1
df_grouped = df.groupby(['Purchase Count', 'Price'], as_index=False).size().rename(columns={'size': 'Total Purchase Value'})
df_grouped['Total Purchase Value'] = df_grouped['Total Purchase Value'] * df_grouped['Price']
df_grouped = df_grouped.rename(columns={'Price': 'Item Price'})
df_grouped = df_grouped[['Purchase Count', 'Item Price', 'Total Purchase Value']]
df_grouped['Purchase Count'] = df_grouped['Purchase Count'].astype(int)
df_grouped['Item Price'] = df_grouped['Item Price'].astype(int)
df_grouped['Total Purchase Value'] = df_grouped['Total Purchase Value'].astype(float)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_59/target_multisource_mcts.csv", index=False)