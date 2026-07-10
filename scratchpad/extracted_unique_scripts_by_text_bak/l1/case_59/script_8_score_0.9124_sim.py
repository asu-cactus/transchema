import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_59/training_0.csv", index_col=0)
df0 = df0.dropna(subset=['PRODUCTLINE', 'SALES'])
df0['SALES'] = pd.to_numeric(df0['SALES'], errors='coerce')
df0 = df0.dropna(subset=['SALES'])
result = df0.groupby('PRODUCTLINE', as_index=False)['SALES'].sum()
result['PRODUCTLINE'] = result['PRODUCTLINE'].astype(str)
result['SALES'] = result['SALES'].astype(float)
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_59/target_multisource_mcts.csv", index=False)