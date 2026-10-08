import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length3_52/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length3_52/training_1.csv', index_col=0)
df2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length3_52/training_2.csv', index_col=0)
df3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length3_52/training_3.csv', index_col=0)

df0 = df0.rename(columns={'businesses': 'businesses_x', 'counts': 'counts_x'})
df1 = df1.rename(columns={'businesses': 'businesses_y', 'counts': 'counts_y'})
df2 = df2.rename(columns={'businesses': 'businesses_x_5', 'counts': 'counts_x_6'})
df3 = df3.rename(columns={'businesses': 'businesses_y_7', 'counts': 'counts_y_8'})

df0['zipcode'] = df0['zipcode'].astype(int)
df1['zipcode'] = df1['zipcode'].astype(int)
df2['zipcode'] = df2['zipcode'].astype(int)
df3['zipcode'] = df3['zipcode'].astype(int)

df0['counts_x'] = df0['counts_x'].astype(int)
df1['counts_y'] = df1['counts_y'].astype(int)
df2['counts_x_6'] = df2['counts_x_6'].astype(int)
df3['counts_y_8'] = df3['counts_y_8'].astype(int)

df0['businesses_x'] = df0['businesses_x'].astype(str)
df1['businesses_y'] = df1['businesses_y'].astype(str)
df2['businesses_x_5'] = df2['businesses_x_5'].astype(str)
df3['businesses_y_7'] = df3['businesses_y_7'].astype(str)

join_01 = pd.merge(df0, df1, on='zipcode', how='outer')
join_012 = pd.merge(join_01, df2, on='zipcode', how='outer')
join_0123 = pd.merge(join_012, df3, on='zipcode', how='outer')

join_0123 = join_0123[['zipcode', 'businesses_x', 'counts_x', 'businesses_y', 'counts_y', 'businesses_x_5', 'counts_x_6', 'businesses_y_7', 'counts_y_8']]

join_0123.to_csv('autopipeline-benchmarks/github-pipelines/length3_52/target_multisource_mcts.csv', index=False)