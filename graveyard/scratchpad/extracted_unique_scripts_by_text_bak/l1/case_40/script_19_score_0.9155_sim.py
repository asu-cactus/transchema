import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_40/training_0.csv", index_col=0)

joined = pd.merge(df, df, on="ORDERNUMBER", suffixes=('_left', '_right'))

grouped = joined.groupby(['CUSTOMERNAME_left', 'ORDERNUMBER'], as_index=False)['QUANTITYORDERED_left'].sum()

grouped.rename(columns={'CUSTOMERNAME_left': 'CUSTOMERNAME', 'QUANTITYORDERED_left': 'QUANTITYORDERED', 'ORDERNUMBER': 'ORDERNUMBER'}, inplace=True)

grouped['ORDERNUMBER'] = grouped['ORDERNUMBER'].astype(int)
grouped['QUANTITYORDERED'] = grouped['QUANTITYORDERED'].fillna(0).astype(int)
grouped['CUSTOMERNAME'] = grouped['CUSTOMERNAME'].astype(str)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_40/target_multisource_mcts.csv", index=False)