import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_59/training_0.csv", index_col=0)
result = df0[['PRODUCTLINE', 'SALES']].copy()
result['PRODUCTLINE'] = result['PRODUCTLINE'].astype(str)
result['SALES'] = pd.to_numeric(result['SALES'], errors='coerce')
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_59/target_multisource_mcts.csv", index=False)