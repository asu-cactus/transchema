import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_59/training_0.csv", index_col=0)
df0_filtered = df0[df0['PRODUCTLINE'].notna() & df0['SALES'].notna()]
result = df0_filtered[['PRODUCTLINE', 'SALES']].copy()
result['PRODUCTLINE'] = result['PRODUCTLINE'].astype(str)
result['SALES'] = result['SALES'].astype(float)
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_59/target_multisource_mcts.csv", index=False)