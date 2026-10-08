import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_64/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_64/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="Mouse ID", how="inner")

# Select relevant columns
result = merged[['Drug', 'Timepoint', 'Mouse ID']]

# Ensure correct types: Drug as string, Timepoint as integer, Mouse ID as string (do NOT convert Mouse ID to numeric)
result['Drug'] = result['Drug'].astype(str)
result['Timepoint'] = pd.to_numeric(result['Timepoint'], errors='coerce').astype('Int64')
result['Mouse ID'] = result['Mouse ID'].astype(str)

# Group by Drug, Timepoint, Mouse ID and count to remove duplicates
grouped = result.groupby(['Drug', 'Timepoint', 'Mouse ID'], as_index=False).agg({'Timepoint':'count'})

# Drop the aggregation column (count) and keep only the grouped keys as final output
final_result = grouped[['Drug', 'Timepoint', 'Mouse ID']]

final_result.to_csv("autopipeline-benchmarks/github-pipelines/length2_64/target_multisource_mcts.csv", index=False)