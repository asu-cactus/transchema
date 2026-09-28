import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_40/training_0.csv", index_col=0)

# Select relevant columns
df = df0[['CUSTOMERNAME', 'ORDERNUMBER', 'QUANTITYORDERED']].copy()

# Convert ORDERNUMBER and QUANTITYORDERED to numeric with coercion
df['ORDERNUMBER'] = pd.to_numeric(df['ORDERNUMBER'], errors='coerce').astype('Int64')
df['QUANTITYORDERED'] = pd.to_numeric(df['QUANTITYORDERED'], errors='coerce').astype('Int64')

# Drop rows with NaN in CUSTOMERNAME or ORDERNUMBER (keys)
df = df.dropna(subset=['CUSTOMERNAME', 'ORDERNUMBER'])

# Group by CUSTOMERNAME and ORDERNUMBER, sum QUANTITYORDERED
df = df.groupby(['CUSTOMERNAME', 'ORDERNUMBER'], as_index=False).agg({'QUANTITYORDERED': 'sum'})

# Ensure ORDERNUMBER and QUANTITYORDERED are integer type
df['ORDERNUMBER'] = df['ORDERNUMBER'].astype('Int64')
df['QUANTITYORDERED'] = df['QUANTITYORDERED'].astype('Int64')

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_40/target_multisource_mcts.csv", index=False)