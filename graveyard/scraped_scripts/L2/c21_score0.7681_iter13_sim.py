import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_21/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_21/training_1.csv", index_col=0)

df0_grouped = df0.groupby(['state', 'date'], as_index=False)['draw_sales'].sum()
df1_grouped = df1.groupby(['state', 'date'], as_index=False)['draw_sales'].sum()

merged = pd.merge(df0_grouped, df1_grouped, on=['state', 'date'], how='outer', suffixes=('_0', '_1'))

merged['draw_sales'] = merged['draw_sales_0'].fillna(0) - merged['draw_sales_1'].fillna(0)
merged['draw_sales'] = merged['draw_sales'].astype(int)
merged['year'] = pd.to_datetime(merged['date']).dt.year

result = merged[['state', 'date', 'draw_sales', 'year']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_21/target_multisource_mcts.csv", index=False)