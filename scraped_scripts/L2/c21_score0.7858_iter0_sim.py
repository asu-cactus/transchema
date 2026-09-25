import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_21/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_21/training_1.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True)

df['state'] = df['state'].astype(str)
df['date'] = df['date'].astype(str)
df['draw_sales'] = df['draw_sales'].astype(float).astype('Int64')

df['year'] = pd.to_datetime(df['date'], errors='coerce').dt.year.astype('Int64')

df = df[['state', 'date', 'draw_sales', 'year']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length2_21/target_multisource_mcts.csv", index=False)