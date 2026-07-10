import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_40/training_0.csv", index_col=0)

# Filter out rows with NaN in key columns
df = df[df['CUSTOMERNAME'].notnull() & df['ORDERNUMBER'].notnull() & df['QUANTITYORDERED'].notnull()]

# Convert ORDERNUMBER and QUANTITYORDERED to int (safe after filtering NaNs)
df['ORDERNUMBER'] = df['ORDERNUMBER'].astype(int)
df['QUANTITYORDERED'] = df['QUANTITYORDERED'].astype(int)

# Group by CUSTOMERNAME and ORDERNUMBER, sum QUANTITYORDERED
df_grouped = df.groupby(['CUSTOMERNAME', 'ORDERNUMBER'], as_index=False)['QUANTITYORDERED'].sum()

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_40/target_multisource_mcts.csv", index=False)