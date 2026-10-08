import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_3.csv", index_col=0)

agg0 = df0.groupby('zipcode').agg({'businesses': 'first', 'counts': 'sum'}).rename(columns={'businesses': 'businesses_x', 'counts': 'counts_x'}).reset_index()
agg1 = df1.groupby('zipcode').agg({'businesses': 'first', 'counts': 'sum'}).rename(columns={'businesses': 'businesses_y', 'counts': 'counts_y'}).reset_index()
agg2 = df2.groupby('zipcode').agg({'businesses': 'first', 'counts': 'sum'}).rename(columns={'businesses': 'businesses_x_5', 'counts': 'counts_x_6'}).reset_index()
agg3 = df3.groupby('zipcode').agg({'businesses': 'first', 'counts': 'sum'}).rename(columns={'businesses': 'businesses_y_7', 'counts': 'counts_y_8'}).reset_index()

join_0 = pd.merge(agg0, agg1, on='zipcode', how='outer')
join_1 = pd.merge(join_0, agg2, on='zipcode', how='outer')
join_2 = pd.merge(join_1, agg3, on='zipcode', how='outer')

join_2['zipcode'] = join_2['zipcode'].astype('Int64')
join_2['counts_x'] = join_2['counts_x'].fillna(0).astype('Int64')
join_2['counts_y'] = join_2['counts_y'].fillna(0).astype('Int64')
join_2['counts_x_6'] = join_2['counts_x_6'].fillna(0).astype('Int64')
join_2['counts_y_8'] = join_2['counts_y_8'].fillna(0).astype('Int64')

join_2.to_csv("autopipeline-benchmarks/github-pipelines/length3_52/target_multisource_mcts.csv", index=False)