import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_40/training_0.csv", index_col=0)

# Convert ORDERNUMBER and QUANTITYORDERED to numeric with nullable integer dtype
df0['ORDERNUMBER'] = pd.to_numeric(df0['ORDERNUMBER'], errors='coerce').astype('Int64')
df0['QUANTITYORDERED'] = pd.to_numeric(df0['QUANTITYORDERED'], errors='coerce').astype('Int64')

# Select relevant columns
df0 = df0[['CUSTOMERNAME', 'ORDERNUMBER', 'QUANTITYORDERED']]

# Drop rows with missing CUSTOMERNAME or ORDERNUMBER because they are keys
df0 = df0.dropna(subset=['CUSTOMERNAME', 'ORDERNUMBER'])

# Group by CUSTOMERNAME and ORDERNUMBER, sum QUANTITYORDERED
df_grouped = df0.groupby(['CUSTOMERNAME', 'ORDERNUMBER'], dropna=False, as_index=False).agg({'QUANTITYORDERED': 'sum'})

# Convert ORDERNUMBER and QUANTITYORDERED to int (non-nullable) if possible
df_grouped['ORDERNUMBER'] = df_grouped['ORDERNUMBER'].astype(int)
df_grouped['QUANTITYORDERED'] = df_grouped['QUANTITYORDERED'].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_40/target_multisource_mcts.csv", index=False)