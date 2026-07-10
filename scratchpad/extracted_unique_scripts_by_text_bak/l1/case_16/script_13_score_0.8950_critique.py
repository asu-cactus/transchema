import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_16/training_0.csv", index_col=0)

# Remove rows with missing CUSTOMERNAME or ORDERNUMBER to avoid counting NaNs
df0 = df0.dropna(subset=['CUSTOMERNAME', 'ORDERNUMBER'])

# Ensure ORDERNUMBER is integer for counting distinct
df0['ORDERNUMBER'] = df0['ORDERNUMBER'].astype(int)

# Group by CUSTOMERNAME and count distinct ORDERNUMBER
result = df0.groupby('CUSTOMERNAME', as_index=False).agg({'ORDERNUMBER': pd.Series.nunique})

# Rename the aggregation column to match target schema (already ORDERNUMBER)
# Ensure types
result['CUSTOMERNAME'] = result['CUSTOMERNAME'].astype(str)
result['ORDERNUMBER'] = result['ORDERNUMBER'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_16/target_multisource_mcts.csv", index=False)