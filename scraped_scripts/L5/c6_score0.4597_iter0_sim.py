import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_6/training_0.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_6/training_2.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_6/training_1.csv", index_col=0)

df0['year'] = pd.to_datetime(df0['date']).dt.year.astype(int)
df2['year'] = pd.to_datetime(df2['date']).dt.year.astype(int)

union_df = pd.concat([df0[['state','year','draw_sales']], df2[['state','year','draw_sales']]], ignore_index=True)

merged = pd.merge(union_df, df1, on=['state','year'], how='inner')

grouped = merged.groupby(['state','year','full_state','pop'], as_index=False)['draw_sales'].sum()

grouped['full_state'] = grouped['full_state'].astype(str)
grouped['state'] = grouped['state'].astype(str)
grouped['year'] = grouped['year'].astype(int)
grouped['draw_sales'] = grouped['draw_sales'].astype(int)
grouped['pop'] = grouped['pop'].astype(int)

grouped.rename(columns={'pop':'pop', 'full_state':'full_state', 'draw_sales':'draw_sales'}, inplace=True)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_6/target_multisource_mcts.csv", index=False)