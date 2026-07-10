import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_16/training_0.csv", index_col=0)
result = df[['CUSTOMERNAME', 'ORDERNUMBER']].copy()
result['ORDERNUMBER'] = pd.to_numeric(result['ORDERNUMBER'], errors='coerce').astype('Int64')
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_16/target_multisource_mcts.csv", index=False)