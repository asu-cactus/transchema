import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_40/training_0.csv", index_col=0)

# The partial plan suggests joining the same table on CUSTOMERNAME, which is redundant here since it's the same table.
# Instead, we interpret this as just grouping by CUSTOMERNAME and ORDERNUMBER and summing QUANTITYORDERED.

df0['ORDERNUMBER'] = pd.to_numeric(df0['ORDERNUMBER'], errors='coerce').astype('Int64')
df0['QUANTITYORDERED'] = pd.to_numeric(df0['QUANTITYORDERED'], errors='coerce').fillna(0).astype(int)
df0['CUSTOMERNAME'] = df0['CUSTOMERNAME'].astype(str)

result = df0.groupby(['CUSTOMERNAME', 'ORDERNUMBER'], dropna=False, as_index=False)['QUANTITYORDERED'].sum()

result = result[['CUSTOMERNAME', 'ORDERNUMBER', 'QUANTITYORDERED']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_40/target_multisource_mcts.csv", index=False)