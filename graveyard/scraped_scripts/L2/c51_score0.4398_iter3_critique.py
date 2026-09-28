import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_51/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_51/training_1.csv", index_col=0)

# Merge on 'Mouse ID' (string)
merged = pd.merge(df1, df0, on='Mouse ID', how='inner')

# Map 'Mouse ID' string to integer IDs (starting from 0 or 1)
merged['Mouse ID'] = pd.factorize(merged['Mouse ID'])[0]

# Select and reorder columns as per target schema
result = merged[['Drug', 'Timepoint', 'Mouse ID']]

# Ensure correct types
result['Drug'] = result['Drug'].astype(str)
result['Timepoint'] = pd.to_numeric(result['Timepoint'], errors='coerce').astype('Int64')
result['Mouse ID'] = result['Mouse ID'].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_51/target_multisource_mcts.csv", index=False)