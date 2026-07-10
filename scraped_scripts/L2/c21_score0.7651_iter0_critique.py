import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_21/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_21/training_1.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True)

df['state'] = df['state'].astype(str)
df['date'] = df['date'].astype(str)

# draw_sales may have float values, sum aggregation requires numeric type
df['draw_sales'] = pd.to_numeric(df['draw_sales'], errors='coerce')

# Group by state and date, sum draw_sales
df = df.groupby(['state', 'date'], as_index=False).agg({'draw_sales': 'sum'})

# Convert draw_sales to integer type
df['draw_sales'] = df['draw_sales'].astype('Int64')

# Extract year from date
df['year'] = pd.to_datetime(df['date'], errors='coerce').dt.year.astype('Int64')

df = df[['state', 'date', 'draw_sales', 'year']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length2_21/target_multisource_mcts.csv", index=False)