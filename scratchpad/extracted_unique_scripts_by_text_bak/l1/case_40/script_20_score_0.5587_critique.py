import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_40/training_0.csv", index_col=0)

# Select relevant columns
df = df[['CUSTOMERNAME', 'ORDERNUMBER', 'QUANTITYORDERED']]

# Drop rows with missing values in these columns
df = df.dropna(subset=['CUSTOMERNAME', 'ORDERNUMBER', 'QUANTITYORDERED'])

# Convert types to match target schema
df['ORDERNUMBER'] = df['ORDERNUMBER'].astype(int)
df['QUANTITYORDERED'] = df['QUANTITYORDERED'].astype(int)
df['CUSTOMERNAME'] = df['CUSTOMERNAME'].astype(str)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_40/target_multisource_mcts.csv", index=False)