import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_21/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_21/training_1.csv", index_col=0)

df0['draw_sales'] = pd.to_numeric(df0['draw_sales'], errors='coerce')
df1['draw_sales'] = pd.to_numeric(df1['draw_sales'], errors='coerce')

merged = pd.merge(df0, df1, left_on=['state', 'date'], right_on=['state', 'date'], suffixes=('_0', '_1'))

grouped = merged.groupby(['state', 'date'], as_index=False).agg({
    'draw_sales_0': 'min',
    'draw_sales_1': 'min'
})

grouped['draw_sales'] = grouped[['draw_sales_0', 'draw_sales_1']].min(axis=1).fillna(0).astype(int)
grouped['year'] = pd.to_datetime(grouped['date'], errors='coerce').dt.year.fillna(0).astype(int)
result = grouped[['state', 'date', 'draw_sales', 'year']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_21/target_multisource_mcts.csv", index=False)