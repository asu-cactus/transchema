import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_40/training_0.csv", index_col=0, on_bad_lines='skip')

df0 = df0[['CUSTOMERNAME', 'ORDERNUMBER', 'QUANTITYORDERED']]

df0['CUSTOMERNAME'] = df0['CUSTOMERNAME'].astype(str).str.strip()

df0['ORDERNUMBER'] = pd.to_numeric(df0['ORDERNUMBER'], errors='coerce')
df0['QUANTITYORDERED'] = pd.to_numeric(df0['QUANTITYORDERED'], errors='coerce')

df0 = df0.dropna(subset=['CUSTOMERNAME', 'ORDERNUMBER', 'QUANTITYORDERED'])

df0['ORDERNUMBER'] = df0['ORDERNUMBER'].astype(int)
df0['QUANTITYORDERED'] = df0['QUANTITYORDERED'].astype(float)

result = df0.groupby(['CUSTOMERNAME', 'ORDERNUMBER'], as_index=False)['QUANTITYORDERED'].sum()

result['QUANTITYORDERED'] = result['QUANTITYORDERED'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_40/target_multisource_mcts.csv", index=False)