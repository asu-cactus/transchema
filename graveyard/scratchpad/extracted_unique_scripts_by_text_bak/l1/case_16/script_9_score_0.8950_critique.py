import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_16/training_0.csv", index_col=0)

# Keep only relevant columns and drop rows with missing CUSTOMERNAME or ORDERNUMBER
df0 = df0[['CUSTOMERNAME', 'ORDERNUMBER']].dropna(subset=['CUSTOMERNAME', 'ORDERNUMBER'])

# Convert ORDERNUMBER to numeric (integer)
df0['ORDERNUMBER'] = pd.to_numeric(df0['ORDERNUMBER'], errors='coerce')
df0 = df0.dropna(subset=['ORDERNUMBER'])
df0['ORDERNUMBER'] = df0['ORDERNUMBER'].astype(int)

# Group by CUSTOMERNAME and count distinct ORDERNUMBER
result = df0.groupby('CUSTOMERNAME', as_index=False)['ORDERNUMBER'].nunique()

# Rename columns to match target schema
result.columns = ['CUSTOMERNAME', 'ORDERNUMBER']

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_16/target_multisource_mcts.csv", index=False)