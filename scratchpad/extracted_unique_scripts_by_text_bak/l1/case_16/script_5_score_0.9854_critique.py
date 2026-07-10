import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_16/training_0.csv", index_col=0)

# Select relevant columns
df = df0[['CUSTOMERNAME', 'ORDERNUMBER']].copy()

# Convert ORDERNUMBER to numeric (integer), coercing errors to NaN
df['ORDERNUMBER'] = pd.to_numeric(df['ORDERNUMBER'], errors='coerce')

# Drop rows with missing CUSTOMERNAME or ORDERNUMBER
df = df.dropna(subset=['CUSTOMERNAME', 'ORDERNUMBER'])

# Group by CUSTOMERNAME and count distinct ORDERNUMBER (count of orders per customer)
result = df.groupby('CUSTOMERNAME', as_index=False).agg({'ORDERNUMBER': 'count'})

# Rename columns to match target schema exactly
result.columns = ['CUSTOMERNAME', 'ORDERNUMBER']

# Convert ORDERNUMBER to integer type
result['ORDERNUMBER'] = result['ORDERNUMBER'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_16/target_multisource_mcts.csv", index=False)