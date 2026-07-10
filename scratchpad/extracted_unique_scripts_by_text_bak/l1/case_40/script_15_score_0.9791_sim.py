import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_40/training_0.csv", index_col=0)

df_grouped = df.groupby(['CUSTOMERNAME', 'ORDERNUMBER'], as_index=False)['QUANTITYORDERED'].sum()

df_grouped['ORDERNUMBER'] = df_grouped['ORDERNUMBER'].astype(int)
df_grouped['QUANTITYORDERED'] = df_grouped['QUANTITYORDERED'].astype(int)
df_grouped['CUSTOMERNAME'] = df_grouped['CUSTOMERNAME'].astype(str)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_40/target_multisource_mcts.csv", index=False)