import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_59/training_0.csv", index_col=0)

df0['PRODUCTLINE'] = df0['PRODUCTLINE'].astype(str).str.strip()
df0['SALES'] = pd.to_numeric(df0['SALES'], errors='coerce')

df0_filtered = df0[df0['PRODUCTLINE'].notnull() & df0['SALES'].notnull()]

result = df0_filtered.groupby('PRODUCTLINE', as_index=False)['SALES'].sum()

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_59/target_multisource_mcts.csv", index=False)