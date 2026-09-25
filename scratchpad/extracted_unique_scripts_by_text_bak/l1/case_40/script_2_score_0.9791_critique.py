import pandas as pd

# Read all source tables (assuming 4 source tables as per typical multi-source scenario)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_40/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_40/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_40/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_40/training_3.csv", index_col=0)

# Select relevant columns from each source
cols = ['CUSTOMERNAME', 'ORDERNUMBER', 'QUANTITYORDERED']
df0 = df0[cols]
df1 = df1[cols]
df2 = df2[cols]
df3 = df3[cols]

# Concatenate (UNION) all source tables
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Drop rows with missing values in key columns or aggregation column
df_all = df_all.dropna(subset=['CUSTOMERNAME', 'ORDERNUMBER', 'QUANTITYORDERED'])

# Convert ORDERNUMBER and QUANTITYORDERED to int
df_all['ORDERNUMBER'] = df_all['ORDERNUMBER'].astype(int)
df_all['QUANTITYORDERED'] = df_all['QUANTITYORDERED'].astype(int)

# Group by CUSTOMERNAME and ORDERNUMBER, sum QUANTITYORDERED
result = df_all.groupby(['CUSTOMERNAME', 'ORDERNUMBER'], as_index=False)['QUANTITYORDERED'].sum()

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_40/target_multisource_mcts.csv", index=False)