import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_59/training_0.csv", index_col=0)

df = pd.concat([df0], ignore_index=True)

df = df[['PRODUCTLINE', 'SALES']]

df['PRODUCTLINE'] = df['PRODUCTLINE'].astype(str)
df['SALES'] = pd.to_numeric(df['SALES'], errors='coerce')

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_59/target_multisource_mcts.csv", index=False)