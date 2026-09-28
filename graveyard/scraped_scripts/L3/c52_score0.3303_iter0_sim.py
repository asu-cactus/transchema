import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_3.csv", index_col=0)

agg_0 = df0.groupby(['zipcode', 'businesses'], as_index=False)['counts'].sum()
agg_0 = agg_0.sort_values(['zipcode', 'counts'], ascending=[True, False])
agg_0 = agg_0.groupby('zipcode').head(1)
agg_0 = agg_0.rename(columns={'businesses': 'businesses_x', 'counts': 'counts_x'})

agg_1 = df1.groupby(['zipcode', 'businesses'], as_index=False)['counts'].sum()
agg_1 = agg_1.sort_values(['zipcode', 'counts'], ascending=[True, False])
agg_1 = agg_1.groupby('zipcode').head(1)
agg_1 = agg_1.rename(columns={'businesses': 'businesses_y', 'counts': 'counts_y'})

join_01 = pd.merge(agg_0, agg_1, on='zipcode', how='outer')

agg_2 = df2.groupby(['zipcode', 'businesses'], as_index=False)['counts'].sum()
agg_2 = agg_2.sort_values(['zipcode', 'counts'], ascending=[True, False])
agg_2 = agg_2.groupby('zipcode').head(1)
agg_2 = agg_2.rename(columns={'businesses': 'businesses_x_5', 'counts': 'counts_x_6'})

join_012 = pd.merge(join_01, agg_2, on='zipcode', how='outer')

agg_3 = df3.groupby(['zipcode', 'businesses'], as_index=False)['counts'].sum()
agg_3 = agg_3.sort_values(['zipcode', 'counts'], ascending=[True, False])
agg_3 = agg_3.groupby('zipcode').head(1)
agg_3 = agg_3.rename(columns={'businesses': 'businesses_y_7', 'counts': 'counts_y_8'})

result = pd.merge(join_012, agg_3, on='zipcode', how='outer')

result = result.astype({
    'zipcode': 'int64',
    'businesses_x': 'string',
    'counts_x': 'Int64',
    'businesses_y': 'string',
    'counts_y': 'Int64',
    'businesses_x_5': 'string',
    'counts_x_6': 'Int64',
    'businesses_y_7': 'string',
    'counts_y_8': 'Int64'
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_52/target_multisource_mcts.csv", index=False)