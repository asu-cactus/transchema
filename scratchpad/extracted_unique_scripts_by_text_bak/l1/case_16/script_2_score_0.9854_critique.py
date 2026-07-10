import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_16/training_0.csv", index_col=0)

# Convert ORDERNUMBER to numeric, coercing errors to NaN
df0['ORDERNUMBER'] = pd.to_numeric(df0['ORDERNUMBER'], errors='coerce')

# Filter out rows with missing CUSTOMERNAME or ORDERNUMBER
df_filtered = df0.dropna(subset=['CUSTOMERNAME', 'ORDERNUMBER'])

# Group by CUSTOMERNAME and count ORDERNUMBER
result = df_filtered.groupby('CUSTOMERNAME', as_index=False).agg({'ORDERNUMBER': 'count'})

# Ensure ORDERNUMBER is integer type
result['ORDERNUMBER'] = result['ORDERNUMBER'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_16/target_multisource_mcts.csv", index=False)