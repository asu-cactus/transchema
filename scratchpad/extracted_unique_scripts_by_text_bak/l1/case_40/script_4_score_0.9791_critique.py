import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_40/training_0.csv", index_col=0)

# Group by CUSTOMERNAME and ORDERNUMBER, sum QUANTITYORDERED
grouped = df.groupby(['CUSTOMERNAME', 'ORDERNUMBER'], as_index=False)['QUANTITYORDERED'].sum()

# Cast types to match target schema
grouped['ORDERNUMBER'] = grouped['ORDERNUMBER'].astype(int)
grouped['QUANTITYORDERED'] = grouped['QUANTITYORDERED'].fillna(0).astype(int)
grouped['CUSTOMERNAME'] = grouped['CUSTOMERNAME'].astype(str)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_40/target_multisource_mcts.csv", index=False)