import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_21/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_21/training_1.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True)

df['year'] = pd.to_datetime(df['date'], errors='coerce').dt.year

df['draw_sales'] = pd.to_numeric(df['draw_sales'], errors='coerce').fillna(0).astype(int)

df = df[['state', 'date', 'draw_sales', 'year']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length2_21/target_multisource_mcts.csv", index=False)