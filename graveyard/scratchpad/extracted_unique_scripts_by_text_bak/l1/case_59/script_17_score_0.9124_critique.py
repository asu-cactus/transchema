import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_59/training_0.csv", index_col=0)
df = df0[['PRODUCTLINE', 'SALES']]
df['PRODUCTLINE'] = df['PRODUCTLINE'].astype(str)
df['SALES'] = pd.to_numeric(df['SALES'], errors='coerce')
df = df.dropna(subset=['PRODUCTLINE', 'SALES'])
df = df.groupby('PRODUCTLINE', as_index=False).agg({'SALES': 'sum'})
df.to_csv("autopipeline-benchmarks/github-pipelines/length1_59/target_multisource_mcts.csv", index=False)