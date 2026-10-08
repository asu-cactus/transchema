import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_6/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_6/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_6/training_2.csv", index_col=0)

df0['date'] = pd.to_datetime(df0['date'])
df2['date'] = pd.to_datetime(df2['date'])

grouped = pd.merge(df0, df1, on='state', how='inner', suffixes=('_0', '_1'))
grouped = pd.merge(grouped, df2, on='state', how='inner', suffixes=('', '_2'))

grouped['date_0'] = grouped['date_0']
grouped['date_2'] = grouped['date']

agg = grouped.groupby(['state', 'date_0', 'full_state', 'date_2'], dropna=False).agg({
    'draw_sales_0': 'sum',
    'draw_sales': 'sum',
    'pop': 'sum',
    'year': 'max'
}).reset_index()

agg['draw_sales'] = agg['draw_sales_0'] + agg['draw_sales']
agg['year'] = agg['year'].astype('Int64')
agg['pop'] = agg['pop'].astype('Int64')
agg['full_state'] = agg['full_state'].astype('Int64', errors='ignore')

result = agg[['state', 'year', 'draw_sales', 'full_state', 'pop']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_6/target_multisource_mcts.csv", index=False)