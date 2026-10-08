import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_59/training_0.csv", index_col=0)
df0 = df0.dropna(subset=['PRODUCTLINE', 'SALES'])
grouped = df0.groupby('PRODUCTLINE', as_index=False)['SALES'].sum()
grouped['SALES'] = grouped['SALES'].astype(float)
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_59/target_multisource_mcts.csv", index=False)