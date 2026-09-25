import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_16/training_0.csv", index_col=0)
df = df0[['CUSTOMERNAME', 'ORDERNUMBER']].copy()
df['ORDERNUMBER'] = pd.to_numeric(df['ORDERNUMBER'], errors='coerce').astype('Int64')
df.to_csv("autopipeline-benchmarks/github-pipelines/length1_16/target_multisource_mcts.csv", index=False)