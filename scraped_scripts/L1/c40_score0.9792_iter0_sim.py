import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_40/training_0.csv", index_col=0)

df0_grouped = df0.groupby(['CUSTOMERNAME', 'ORDERNUMBER'], as_index=False)['QUANTITYORDERED'].sum()

df0_grouped['ORDERNUMBER'] = df0_grouped['ORDERNUMBER'].astype(int)
df0_grouped['QUANTITYORDERED'] = df0_grouped['QUANTITYORDERED'].astype(int)
df0_grouped['CUSTOMERNAME'] = df0_grouped['CUSTOMERNAME'].astype(str)

df0_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_40/target_multisource_mcts.csv", index=False)