import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_21/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_21/training_1.csv", index_col=0)

# Join on ['state', 'date']
df = pd.merge(df0, df1, on=['state', 'date'], how='inner', suffixes=('_0', '_1'))

# Sum draw_sales columns from both sources
df['draw_sales'] = df['draw_sales_0'].astype('Int64') + df['draw_sales_1'].astype('Int64')

# Extract year from date
df['year'] = pd.to_datetime(df['date']).dt.year.astype('Int64')

# Group by state, date, year and sum draw_sales (in case of duplicates)
df = df.groupby(['state', 'date', 'year'], as_index=False).agg({'draw_sales': 'sum'})

# Ensure draw_sales is integer type
df['draw_sales'] = df['draw_sales'].astype('Int64')

df = df[['state', 'date', 'draw_sales', 'year']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length2_21/target_multisource_mcts.csv", index=False)