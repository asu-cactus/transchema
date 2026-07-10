import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_40/training_0.csv", index_col=0)

# Filter out rows with missing values in key columns or aggregation column
df0 = df0.dropna(subset=['CUSTOMERNAME', 'ORDERNUMBER', 'QUANTITYORDERED'])

# Group by CUSTOMERNAME and ORDERNUMBER, summing QUANTITYORDERED
df_grouped = df0.groupby(['CUSTOMERNAME', 'ORDERNUMBER'], as_index=False)['QUANTITYORDERED'].sum()

# Convert ORDERNUMBER and QUANTITYORDERED to integer as per target schema
df_grouped['ORDERNUMBER'] = df_grouped['ORDERNUMBER'].astype(int)
df_grouped['QUANTITYORDERED'] = df_grouped['QUANTITYORDERED'].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_40/target_multisource_mcts.csv", index=False)