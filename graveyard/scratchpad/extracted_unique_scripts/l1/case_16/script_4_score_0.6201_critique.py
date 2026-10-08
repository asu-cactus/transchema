import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_16/training_0.csv", index_col=0)

# Select relevant columns and convert ORDERNUMBER to integer type
df0['ORDERNUMBER'] = pd.to_numeric(df0['ORDERNUMBER'], errors='coerce').astype('Int64')

# Drop rows with missing CUSTOMERNAME or ORDERNUMBER
df0 = df0.dropna(subset=['CUSTOMERNAME', 'ORDERNUMBER'])

# Group by CUSTOMERNAME and ORDERNUMBER to get unique pairs
result = df0[['CUSTOMERNAME', 'ORDERNUMBER']].drop_duplicates().reset_index(drop=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_16/target_multisource_mcts.csv", index=False)