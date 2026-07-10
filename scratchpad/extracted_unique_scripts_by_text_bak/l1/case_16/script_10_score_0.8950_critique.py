import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_16/training_0.csv", index_col=0)

# Filter out rows with missing CUSTOMERNAME or ORDERNUMBER
df_filtered = df[df['CUSTOMERNAME'].notnull() & df['ORDERNUMBER'].notnull()]

# Convert ORDERNUMBER to numeric (integer)
df_filtered['ORDERNUMBER'] = pd.to_numeric(df_filtered['ORDERNUMBER'], errors='coerce')
df_filtered = df_filtered[df_filtered['ORDERNUMBER'].notnull()]

# Group by CUSTOMERNAME and count distinct ORDERNUMBER
result = df_filtered.groupby('CUSTOMERNAME', as_index=False).agg({'ORDERNUMBER': pd.Series.nunique})

# Rename columns to match target schema exactly
result.columns = ['CUSTOMERNAME', 'ORDERNUMBER']

# Convert ORDERNUMBER to integer type
result['ORDERNUMBER'] = result['ORDERNUMBER'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_16/target_multisource_mcts.csv", index=False)