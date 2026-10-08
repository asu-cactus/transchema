import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_40/training_0.csv", index_col=0)

df0 = df0[['CUSTOMERNAME', 'ORDERNUMBER', 'QUANTITYORDERED']]

df0['ORDERNUMBER'] = pd.to_numeric(df0['ORDERNUMBER'], errors='coerce').astype('Int64')
df0['QUANTITYORDERED'] = pd.to_numeric(df0['QUANTITYORDERED'], errors='coerce').astype('Int64')
df0['CUSTOMERNAME'] = df0['CUSTOMERNAME'].astype(str)

df0.to_csv("autopipeline-benchmarks/github-pipelines/length1_40/target_multisource_mcts.csv", index=False)