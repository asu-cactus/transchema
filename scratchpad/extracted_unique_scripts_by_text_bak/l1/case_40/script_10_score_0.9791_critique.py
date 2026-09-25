import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_40/training_0.csv", index_col=0)

df = df[['CUSTOMERNAME', 'ORDERNUMBER', 'QUANTITYORDERED']]

df['ORDERNUMBER'] = pd.to_numeric(df['ORDERNUMBER'], errors='coerce').astype('Int64')
df['QUANTITYORDERED'] = pd.to_numeric(df['QUANTITYORDERED'], errors='coerce').astype('Int64')
df['CUSTOMERNAME'] = df['CUSTOMERNAME'].astype(str)

df = df.dropna(subset=['CUSTOMERNAME', 'ORDERNUMBER', 'QUANTITYORDERED'])

df = df.groupby(['CUSTOMERNAME', 'ORDERNUMBER'], as_index=False).agg({'QUANTITYORDERED': 'sum'})

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_40/target_multisource_mcts.csv", index=False)